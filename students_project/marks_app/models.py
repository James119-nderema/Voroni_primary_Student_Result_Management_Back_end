from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta


class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    class_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.class_name}"


class StudentMarks(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    math_marks = models.IntegerField()
    english_marks = models.IntegerField()
    kiswahili_marks = models.IntegerField()
    science_marks = models.IntegerField()
    sst_marks = models.IntegerField()
    total_marks = models.IntegerField()
    submission_date = models.DateField(default=timezone.now)

    class Meta:
        verbose_name = "Student Marks"
        verbose_name_plural = "Student Marks"

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - Total: {self.total_marks}"

    def clean(self):
        # Check if there's a previous submission for this student
        if not self.id:  # Only check for new records
            previous_submission = StudentMarks.objects.filter(student=self.student).order_by('-submission_date').first()

            if previous_submission:
                today = timezone.now().date()
                days_since_last_submission = (today - previous_submission.submission_date).days
                days_remaining = 7 - days_since_last_submission

                if days_since_last_submission < 7:
                    raise ValidationError({
                        'student': f"Cannot submit marks for this student. Previous submission was {days_since_last_submission} days ago. Please wait {days_remaining} more days."
                    })

    def save(self, *args, **kwargs):
        # Run validation
        self.clean()

        # Calculate total marks if not provided
        if not self.total_marks:
            self.total_marks = (
                    self.math_marks +
                    self.english_marks +
                    self.kiswahili_marks +
                    self.science_marks +
                    self.sst_marks
            )

        # Save only the date part without time
        if not self.id:  # Only set the date for new records
            today = timezone.now().date()
            self.submission_date = today

        super().save(*args, **kwargs)