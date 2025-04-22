from django.contrib import admin
from .models import StudentMarks

@admin.register(StudentMarks)
class StudentMarksAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'total_marks', 'submission_date')
    list_filter = ('submission_date',)
    search_fields = ('student_id',)
    date_hierarchy = 'submission_date'
