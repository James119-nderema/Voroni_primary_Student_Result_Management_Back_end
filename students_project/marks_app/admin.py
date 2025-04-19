from django.contrib import admin
from .models import StudentMarks

@admin.register(StudentMarks)
class StudentMarksAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'marks', 'submission_date')
    list_filter = ('submission_date',)
    search_fields = ('student__first_name', 'student__last_name')
    date_hierarchy = 'submission_date'