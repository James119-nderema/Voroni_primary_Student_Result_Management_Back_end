from rest_framework import serializers
from .models import StudentMarks
from students_app.models import Student

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name', 'class_name']

class StudentMarksSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentMarks
        fields = ['id', 'submission_date', 'math', 'eng', 'kis', 'sci', 'sst', 'total_marks']