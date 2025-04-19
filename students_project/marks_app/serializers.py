# serializers.py

from rest_framework import serializers
from .models import Student, StudentMarks
from django.utils import timezone
from django.core.exceptions import ValidationError


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name', 'class_name']


class StudentMarksSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    class_name = serializers.SerializerMethodField()

    class Meta:
        model = StudentMarks
        fields = [
            'id', 'student', 'student_name', 'class_name',
            'math_marks', 'english_marks', 'kiswahili_marks',
            'science_marks', 'sst_marks', 'total_marks',
            'submission_date'
        ]

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"

    def get_class_name(self, obj):
        return obj.student.class_name


class StudentMarksCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    subject_marks = serializers.DictField(write_only=True)

    class Meta:
        model = StudentMarks
        fields = ['id', 'subject_marks', 'total_marks']
        extra_kwargs = {
            'total_marks': {'required': False}
        }

    def create(self, validated_data, class_name=None):
        student_id = validated_data.pop('id')
        subject_marks = validated_data.pop('subject_marks', {})
        total_marks = validated_data.get('total_marks', 0)

        # Try to get the student, create a placeholder if not found
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            # Create a placeholder student with the ID
            student = Student.objects.create(
                id=student_id,
                first_name=f"Student",
                last_name=f"{student_id}",
                class_name=f"{class_name}"
            )

        # Check if a submission for this student is allowed (7-day rule)
        previous_submission = StudentMarks.objects.filter(student=student).order_by('-submission_date').first()

        if previous_submission:
            today = timezone.now().date()
            days_since_last_submission = (today - previous_submission.submission_date).days
            days_remaining = 7 - days_since_last_submission

            if days_since_last_submission < 7:
                raise serializers.ValidationError({
                    'student': f"Cannot submit marks for student {student_id}. Previous submission was {days_since_last_submission} days ago. Please wait {days_remaining} more days."
                })

        # Create StudentMarks instance
        student_marks = StudentMarks(
            student=student,
            math_marks=subject_marks.get('Math', 0),
            english_marks=subject_marks.get('Eng', 0),
            kiswahili_marks=subject_marks.get('Kis', 0),
            science_marks=subject_marks.get('Sci', 0),
            sst_marks=subject_marks.get('SST', 0),
            total_marks=total_marks
        )
        student_marks.save()

        return student_marks


class BatchStudentMarksCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    subject_marks = serializers.DictField()
    total_marks = serializers.FloatField(required=False)


class BatchMarksSubmissionSerializer(serializers.Serializer):
    marks = BatchStudentMarksCreateSerializer(many=True)

    def create(self, validated_data, class_name=None):
        results = []
        errors = []
        marks_data = validated_data.get('marks', [])

        for mark_data in marks_data:
            student_id = mark_data.get('id')
            subject_marks = mark_data.get('subject_marks', {})
            total_marks = mark_data.get('total_marks', 0)

            # Try to get the student, create a placeholder if not found
            try:
                student = Student.objects.get(id=student_id)
            except Student.DoesNotExist:
                # Create a placeholder student with the ID
                student = Student.objects.create(
                    id=student_id,
                    first_name=f"Student",
                    last_name=f"{student_id}",
                    class_name=f"{class_name}"
                )

            # Check if a submission for this student is allowed (7-day rule)
            previous_submission = StudentMarks.objects.filter(student=student).order_by('-submission_date').first()

            if previous_submission:
                today = timezone.now().date()
                days_since_last_submission = (today - previous_submission.submission_date).days
                days_remaining = 7 - days_since_last_submission

                if days_since_last_submission < 7:
                    errors.append({
                        'student_id': student_id,
                        'error': f"Cannot submit marks for student {student_id}. Previous submission was {days_since_last_submission} days ago. Please wait {days_remaining} more days."
                    })
                    continue

            try:
                student_marks = StudentMarks(
                    student=student,
                    math_marks=subject_marks.get('Math', 0),
                    english_marks=subject_marks.get('Eng', 0),
                    kiswahili_marks=subject_marks.get('Kis', 0),
                    science_marks=subject_marks.get('Sci', 0),
                    sst_marks=subject_marks.get('SST', 0),
                    total_marks=total_marks
                )
                student_marks.save()
                results.append(student_marks)
            except Exception as e:
                errors.append({
                    'student_id': student_id,
                    'error': str(e)
                })

        if errors:
            raise serializers.ValidationError(errors)

        return results