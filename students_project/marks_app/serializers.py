from rest_framework import serializers
from .models import StudentMarks


class StudentMarksSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = StudentMarks
        fields = ['id', 'student_id', 'marks', 'submission_date']
        read_only_fields = ['submission_date']

    def create(self, validated_data):
        return StudentMarks.objects.create(**validated_data)