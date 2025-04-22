# pdf_reports/admin.py
from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'report_type', 'class_name', 'student_id', 'generated_at', 'generated_by', 'download_count')
    list_filter = ('report_type', 'generated_at')
    search_fields = ('class_name', 'student_id', 'generated_by__username')
    readonly_fields = ('download_count',)

    def has_change_permission(self, request, obj=None):
        # Reports should not be editable
        return False