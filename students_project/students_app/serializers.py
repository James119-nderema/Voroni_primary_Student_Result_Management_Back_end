from rest_framework import serializers
from students_app.models import Student
from .models import ClassDetails

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name', 'student_id','class_name']

# Add this to your existing serializers.py
class ClassDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassDetails
        fields = ['class_name','class_teacher']

