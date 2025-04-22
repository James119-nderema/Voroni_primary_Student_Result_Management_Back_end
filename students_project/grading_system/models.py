from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta


class StudentMarks(models.Model):
    student_id = models.IntegerField()
    math = models.IntegerField()
    eng = models.IntegerField()
    kis = models.IntegerField()
    sci = models.IntegerField()
    sst = models.IntegerField()
    total_marks = models.IntegerField()
    submission_date = models.DateField(default=timezone.now)

    class Meta:
        verbose_name = 'Student Mark'
        verbose_name_plural = 'Student Marks'

    def __str__(self):
        return f"Student #{self.student_id} - {self.submission_date}"