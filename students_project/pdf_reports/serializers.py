# pdf_reports/serializers.py
from rest_framework import serializers
from .models import Report
from students_app.models import Student
from grading_system.models import StudentMarks


class ReportSerializer(serializers.ModelSerializer):
    """Serializer for Report model"""
    generated_by_name = serializers.ReadOnlyField(source='generated_by.username')

    class Meta:
        model = Report
        fields = ['id', 'report_type', 'class_name', 'student_id', 'generated_at',
                  'generated_by', 'generated_by_name', 'download_count', 'file_path']
        read_only_fields = ['generated_at', 'download_count', 'file_path']


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for Student model"""

    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name', 'class_name']


class StudentMarksSerializer(serializers.ModelSerializer):
    """Serializer for StudentMarks model"""

    class Meta:
        model = StudentMarks
        fields = ['id', 'student', 'subject', 'marks', 'term', 'year']