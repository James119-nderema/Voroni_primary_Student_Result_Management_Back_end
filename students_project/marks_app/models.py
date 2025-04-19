from django.db import models
from django.utils import timezone

class StudentMarks(models.Model):
    # ForeignKey to the existing students table
    student = models.ForeignKey('students_app.Student', on_delete=models.CASCADE, related_name='marks')
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    submission_date = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'student_marks'
        verbose_name = 'Student Mark'
        verbose_name_plural = 'Student Marks'

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.marks}"