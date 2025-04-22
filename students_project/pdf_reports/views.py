# pdf_reports/views.py
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, FileResponse
from django.utils import timezone
from django.views.decorators.http import require_GET
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from io import BytesIO
import os
from django.conf import settings

from students_app.models import Student
from grading_system.models import StudentMarks
# Import the Report model from models.py instead of defining it here
from .models import Report
from .utils import process_student_marks, render_to_pdf, save_pdf


def generate_results_report(request, report_type='all', class_name=None, student_id=None):
    """Generate and save PDF report based on report type"""
    title = "Student Results Report"

    # Get students based on report type
    if report_type == 'student' and student_id:
        student = get_object_or_404(Student, id=student_id)
        students = [student]
        title = f"Results Report for {student.first_name} {student.last_name}"
        filename = f"student_{student_id}_report"
    elif report_type == 'class' and class_name:
        students = Student.objects.filter(class_name=class_name).order_by('first_name', 'last_name')
        title = f"Results Report for Class {class_name}"
        filename = f"class_{class_name}_report"
    else:
        students = Student.objects.all().order_by('class_name', 'first_name', 'last_name')
        filename = "all_students_report"

    # Group students by class
    class_groups = {}

    for student in students:
        # Get all marks for this student
        marks = StudentMarks.objects.filter(student_id=student.id)

        if not marks.exists():
            continue  # Skip students with no marks

        current_class = student.class_name

        if current_class not in class_groups:
            class_groups[current_class] = []

        student_data = process_student_marks(student, marks)
        class_groups[current_class].append(student_data)

    # Prepare context for the template
    context = {
        'title': title,
        'class_groups': class_groups,
        'today': timezone.now(),
    }

    # Generate PDF
    pdf_file = render_to_pdf('student_results_pdf.html', context)

    if pdf_file:
        # Save PDF to disk
        file_path = save_pdf(BytesIO(pdf_file.getvalue()), filename)

        # Create report record
        report = Report.objects.create(
            report_type=report_type,
            class_name=class_name,
            student_id=student_id,
            generated_by=request.user if request.user.is_authenticated else None,
            file_path=file_path
        )

        # Return PDF as response
        response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'

        # Update download count
        report.download_count += 1
        report.save()

        return response

    return HttpResponse('Error generating PDF', status=400)


@require_GET
def download_all_results(request):
    """Download results for all students"""
    return generate_results_report(request, report_type='all')


@require_GET
def download_class_results(request, class_name):
    """Download results for a specific class"""
    return generate_results_report(request, report_type='class', class_name=class_name)


@require_GET
def download_student_results(request, student_id):
    """Download results for a specific student"""
    return generate_results_report(request, report_type='student', student_id=student_id)


@require_GET
def download_saved_report(request, report_id):
    """Download a previously generated report"""
    report = get_object_or_404(Report, id=report_id)

    # Check if file exists
    file_path = os.path.join(settings.MEDIA_ROOT, report.file_path)
    if not os.path.exists(file_path):
        return HttpResponse('Report file not found', status=404)

    # Update download count
    report.download_count += 1
    report.save()

    # Return file response
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))


# API views
@api_view(['GET'])
@permission_classes([AllowAny])
def api_get_reports(request):
    """API endpoint to get all reports"""
    reports = Report.objects.all()
    from .serializers import ReportSerializer
    serializer = ReportSerializer(reports, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_download_report(request, report_id):
    """API endpoint to download a report"""
    report = get_object_or_404(Report, id=report_id)

    # Check if file exists
    file_path = os.path.join(settings.MEDIA_ROOT, report.file_path)
    if not os.path.exists(file_path):
        return Response({'error': 'Report file not found'}, status=status.HTTP_404_NOT_FOUND)

    # Update download count
    report.download_count += 1
    report.save()

    # Return file response
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))