# admin.py

from django.contrib import admin
from .models import Student, StudentMarks


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'class_name')
    search_fields = ('first_name', 'last_name', 'class_name')
    list_filter = ('class_name',)


@admin.register(StudentMarks)
class StudentMarksAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'get_student_name', 'get_class_name',
        'math_marks', 'english_marks', 'kiswahili_marks',
        'science_marks', 'sst_marks', 'total_marks',
        'submission_date'
    )
    list_filter = ('submission_date',)
    search_fields = ('student__first_name', 'student__last_name', 'student__class_name')
    date_hierarchy = 'submission_date'

    def get_student_name(self, obj):
        return f"{obj.student.first_name} {obj.student.last_name}"

    get_student_name.short_description = 'Student Name'

    def get_class_name(self, obj):
        return obj.student.class_name

    get_class_name.short_description = 'Class'