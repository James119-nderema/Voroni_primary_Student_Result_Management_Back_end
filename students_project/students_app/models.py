from django.db import models
from django.utils import timezone


class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    # If your field is called 'class' in the database,
    # Django model will refer to it as 'class_name' or similar
    student_id = models.CharField(max_length=50)  # Using class_name instead of 'class'
    class_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id}) {self.class_name}"



class ClassDetails(models.Model):
    """
    Model to store class details
    """
    class_name = models.CharField(max_length=100)
    class_teacher = models.CharField(max_length=50)
    #class_teacher = models.CharField(max_length=100)
    #classroom = models.CharField(max_length=50, null=True, blank=True)
    #capacity = models.IntegerField(default=0)
    #description = models.TextField(null=True, blank=True)
    #created_at = models.DateTimeField(auto_now_add=True)
    #updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Class Detail"
        verbose_name_plural = "Class Details"

    def __str__(self):
        return self.class_name


