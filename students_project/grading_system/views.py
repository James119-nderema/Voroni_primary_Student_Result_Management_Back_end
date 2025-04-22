# views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import StudentMarks
from students_app.models import Student  # Import the Student model from students_app


@csrf_exempt
def submit_grades(request):
    if request.method != 'POST':
        return JsonResponse({'detail': 'Only POST method is allowed'}, status=405)

    try:
        data = json.loads(request.body)
        if 'marks' not in data or not isinstance(data['marks'], list):
            return JsonResponse({'detail': 'Invalid data format. Expected "marks" list.'}, status=400)

        marks_data = data['marks']

        # Lists to track submissions
        successful_submissions = []
        failed_submissions = []

        # Process each student's marks
        for mark in marks_data:
            student_id = mark.get('id')
            subject_marks = mark.get('subject_marks', {})
            total_marks = mark.get('total_marks', 0)

            # Validate required fields
            if not student_id:
                failed_submissions.append({
                    'id': student_id,
                    'error': 'Missing student ID'
                })
                continue

            # Check if student exists in students_app_student
            try:
                student = Student.objects.get(id=student_id)
            except Student.DoesNotExist:
                failed_submissions.append({
                    'id': student_id,
                    'error': f'Student with ID {student_id} does not exist'
                })
                continue

            # Check for missing subjects
            required_subjects = ['Math', 'Eng', 'Kis', 'Sci', 'SST']
            missing_subjects = [subject for subject in required_subjects if subject not in subject_marks]
            if missing_subjects:
                failed_submissions.append({
                    'id': student_id,
                    'error': f'Missing marks for subjects: {", ".join(missing_subjects)}'
                })
                continue

            # Calculate total marks if not provided
            if not total_marks:
                total_marks = sum(subject_marks.values())

            # Check 7-day rule: Cannot submit new grades within 7 days of previous submission
            today = timezone.now().date()
            previous_submission = StudentMarks.objects.filter(student_id=student_id).order_by(
                '-submission_date').first()

            if previous_submission:
                days_since_last_submission = (today - previous_submission.submission_date).days
                if days_since_last_submission < 7:
                    failed_submissions.append({
                        'id': student_id,
                        'name': f"{student.first_name} {student.last_name}",
                        'error': f'Cannot submit new grades within 7 days of the previous submission. Last submission: {previous_submission.submission_date.strftime("%Y-%m-%d")}'
                    })
                    continue

            # All validation passed, create the marks record
            try:
                with transaction.atomic():
                    new_marks = StudentMarks(
                        student_id=student_id,
                        math=subject_marks['Math'],
                        eng=subject_marks['Eng'],
                        kis=subject_marks['Kis'],
                        sci=subject_marks['Sci'],
                        sst=subject_marks['SST'],
                        total_marks=total_marks,
                        submission_date=today
                    )
                    new_marks.save()

                    successful_submissions.append({
                        'id': student_id,
                        'name': f"{student.first_name} {student.last_name}"
                    })
            except Exception as e:
                failed_submissions.append({
                    'id': student_id,
                    'error': str(e)
                })

        # Determine the response status based on submissions
        if not successful_submissions and failed_submissions:
            # If all submissions failed, return error status
            return JsonResponse({
                'detail': 'All submissions failed',
                'errors': failed_submissions,
                'submitted': []
            }, status=400)
        elif failed_submissions:
            # If some submissions failed, return partial success
            return JsonResponse({
                'detail': 'Some submissions were successful',
                'errors': failed_submissions,
                'submitted': successful_submissions
            }, status=207)  # 207 Multi-Status
        else:
            # If all submissions succeeded
            return JsonResponse({
                'detail': 'All grades submitted successfully',
                'submitted': successful_submissions
            }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'detail': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'detail': str(e)}, status=500)


def get_student_marks(request):
    student_id = request.GET.get('id')

    if not student_id:
        return JsonResponse({'detail': 'Student ID is required'}, status=400)

    try:
        # First check if student exists
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return JsonResponse({'detail': f'Student with ID {student_id} does not exist'}, status=404)

        # Get all marks for this student, ordered by submission date (newest first)
        marks = StudentMarks.objects.filter(student_id=student_id).order_by('-submission_date')

        if not marks:
            return JsonResponse({'detail': 'No marks found for this student'}, status=404)

        # Format the response
        marks_data = []
        for mark in marks:
            marks_data.append({
                'id': mark.id,
                'math': mark.math,
                'eng': mark.eng,
                'kis': mark.kis,
                'sci': mark.sci,
                'sst': mark.sst,
                'total_marks': mark.total_marks,
                'submission_date': mark.submission_date.strftime('%Y-%m-%d')
            })

        return JsonResponse({
            'student': {
                'id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'class_name': student.class_name
            },
            'marks': marks_data
        })
    except Exception as e:
        return JsonResponse({'detail': str(e)}, status=500)


def get_class_marks(request):
    class_name = request.GET.get('class_name')

    if not class_name:
        return JsonResponse({'detail': 'Class name is required'}, status=400)

    try:
        # Get all students in this class
        students = Student.objects.filter(class_name=class_name)

        if not students:
            return JsonResponse({'detail': 'No students found in this class'}, status=404)

        # Get the latest marks for each student
        class_data = []

        for student in students:
            latest_mark = StudentMarks.objects.filter(student_id=student.id).order_by('-submission_date').first()

            student_data = {
                'id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'marks': None
            }

            if latest_mark:
                student_data['marks'] = {
                    'math': latest_mark.math,
                    'eng': latest_mark.eng,
                    'kis': latest_mark.kis,
                    'sci': latest_mark.sci,
                    'sst': latest_mark.sst,
                    'total_marks': latest_mark.total_marks,
                    'submission_date': latest_mark.submission_date.strftime('%Y-%m-%d')
                }

            class_data.append(student_data)

        return JsonResponse({
            'class_name': class_name,
            'students': class_data
        })
    except Exception as e:
        return JsonResponse({'detail': str(e)}, status=500)


def get_all_student_marks(request):
    """
    API endpoint to get all student marks.
    This view supports the frontend's data requirements for the StudentMarksPage component.
    """
    try:
        # Get all marks, ordered by submission date (newest first)
        all_marks = StudentMarks.objects.all().order_by('-submission_date')

        # Format the response to match the frontend expectations
        marks_data = []
        for mark in all_marks:
            # Check for None values and provide defaults
            math_marks = mark.math if mark.math is not None else None
            english_marks = mark.eng if mark.eng is not None else None
            kiswahili_marks = mark.kis if mark.kis is not None else None
            science_marks = mark.sci if mark.sci is not None else None
            sst_marks = mark.sst if mark.sst is not None else None

            marks_data.append({
                'id': mark.id,
                'student': mark.student_id,  # Foreign key to student
                'math_marks': math_marks,  # Match frontend field naming
                'english_marks': english_marks,  # Match frontend field naming
                'kiswahili_marks': kiswahili_marks,  # Match frontend field naming
                'science_marks': science_marks,  # Match frontend field naming
                'sst_marks': sst_marks,  # Match frontend field naming
                'total_marks': mark.total_marks,
                'submission_date': mark.submission_date.strftime('%Y-%m-%d') if mark.submission_date else None
            })

        return JsonResponse(marks_data, safe=False)
    except Exception as e:
        return JsonResponse({'detail': str(e)}, status=500)

def get_all_student_marks(request):
    """
    API endpoint to get all student marks.
    This view supports the frontend's data requirements for the StudentMarksPage component.
    """
    try:
        # Get all marks, ordered by submission date (newest first)
        all_marks = StudentMarks.objects.all().order_by('-submission_date')

        # Format the response to match the frontend expectations
        marks_data = []
        for mark in all_marks:
            # Check for None values and provide defaults
            math_marks = mark.math if mark.math is not None else None
            english_marks = mark.eng if mark.eng is not None else None
            kiswahili_marks = mark.kis if mark.kis is not None else None
            science_marks = mark.sci if mark.sci is not None else None
            sst_marks = mark.sst if mark.sst is not None else None

            # Look up student details
            try:
                student = Student.objects.get(id=mark.student_id)
                student_exists = True
                student_class = student.class_name
            except Student.DoesNotExist:
                student_exists = False
                student_class = None

            marks_data.append({
                'id': mark.id,
                'student': mark.student_id,  # Foreign key to student
                'student_exists': student_exists,  # Flag to indicate if student exists
                'class_name': student_class,  # Include class name directly with marks
                'math_marks': math_marks,
                'english_marks': english_marks,
                'kiswahili_marks': kiswahili_marks,
                'science_marks': science_marks,
                'sst_marks': sst_marks,
                'total_marks': mark.total_marks,
                'submission_date': mark.submission_date.strftime('%Y-%m-%d') if mark.submission_date else None
            })

        return JsonResponse(marks_data, safe=False)
    except Exception as e:
        return JsonResponse({'detail': str(e)}, status=500)
@csrf_exempt
def update_student_marks(request):
        """
        API endpoint to update student marks.
        This view supports the frontend's ability to edit marks via the EditMarksPopup component.
        """
        if request.method != 'POST':
            return JsonResponse({'detail': 'Only POST method is allowed'}, status=405)

        try:
            data = json.loads(request.body)
            student_id = data.get('student')
            mark_id = data.get('id')

            # Validate required fields
            if not student_id:
                return JsonResponse({'detail': 'Missing student ID'}, status=400)

            # Check if student exists
            try:
                student = Student.objects.get(id=student_id)
            except Student.DoesNotExist:
                return JsonResponse({'detail': f'Student with ID {student_id} does not exist'}, status=404)

            # Get existing mark record or create new one
            if mark_id:
                try:
                    mark = StudentMarks.objects.get(id=mark_id)
                except StudentMarks.DoesNotExist:
                    return JsonResponse({'detail': f'Mark record with ID {mark_id} does not exist'}, status=404)
            else:
                # Create new mark record
                mark = StudentMarks(student_id=student_id, submission_date=timezone.now().date())

            # Update mark fields
            mark.math = data.get('math_marks', mark.math)
            mark.eng = data.get('english_marks', mark.eng)
            mark.kis = data.get('kiswahili_marks', mark.kis)
            mark.sci = data.get('science_marks', mark.sci)
            mark.sst = data.get('sst_marks', mark.sst)

            # Calculate total marks
            mark.total_marks = sum(filter(None, [mark.math, mark.eng, mark.kis, mark.sci, mark.sst]))

            # Save the updated mark
            mark.save()

            return JsonResponse({
                'detail': 'Marks updated successfully',
                'id': mark.id,
                'student': mark.student_id,
                'math_marks': mark.math,
                'english_marks': mark.eng,
                'kiswahili_marks': mark.kis,
                'science_marks': mark.sci,
                'sst_marks': mark.sst,
                'total_marks': mark.total_marks,
                'submission_date': mark.submission_date.strftime('%Y-%m-%d') if mark.submission_date else None
            })
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'detail': str(e)}, status=500)