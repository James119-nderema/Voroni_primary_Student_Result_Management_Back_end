# pdf_reports/models.py
from django.db import models
from django.utils import timezone


class Report(models.Model):
    """Model to track generated reports"""
    REPORT_TYPES = (
        ('all', 'All Students'),
        ('class', 'Class Report'),
        ('student', 'Student Report'),
    )

    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    class_name = models.CharField(max_length=100, blank=True, null=True)
    student_id = models.IntegerField(blank=True, null=True)
    generated_at = models.DateTimeField(default=timezone.now)
    generated_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True,
                                     related_name='generated_reports')
    download_count = models.IntegerField(default=0)
    file_path = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-generated_at']
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'

    def __str__(self):
        if self.report_type == 'all':
            return f"All Students Report ({self.generated_at.strftime('%Y-%m-%d %H:%M')})"
        elif self.report_type == 'class':
            return f"Class {self.class_name} Report ({self.generated_at.strftime('%Y-%m-%d %H:%M')})"
        else:
            return f"Student {self.student_id} Report ({self.generated_at.strftime('%Y-%m-%d %H:%M')})"