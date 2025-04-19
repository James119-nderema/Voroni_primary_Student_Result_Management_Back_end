from students_app import views
from django.urls import path, include


urlpatterns = [
    # Student URLs
    path('api/students/', views.student_list, name='student-list'),
    path('api/students/<int:pk>/', views.student_detail, name='student-detail'),
    path('api/students/add/', views.add_student, name='add-student'),

    # Class URLs
    path('api/classes/', views.class_list, name='class-list'),
    path('api/classes/<int:pk>/', views.class_detail, name='class-detail'),
    path('api/classes/add/', views.add_class, name='add-class'),


]


