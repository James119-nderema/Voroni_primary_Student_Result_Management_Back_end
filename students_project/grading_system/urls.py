from django.urls import path
from grading_system import views


urlpatterns = [
    path('api/student-marks/submit_grades/', views.submit_grades, name='submit_grades'),
    path('api/student-marks/get_by_student/', views.get_student_marks, name='get_student_marks'),
    path('api/student-marks/get_by_class/', views.get_class_marks, name='get_class_marks'),
    path('api/student-marks/', views.get_all_student_marks, name='get_all_student_marks'),
    path('api/student-marks/update_student_marks/', views.update_student_marks, name='update_student_marks'),
]