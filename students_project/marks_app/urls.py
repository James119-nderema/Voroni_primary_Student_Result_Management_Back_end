# marks_app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StudentViewSet, StudentMarksViewSet, submit_grades

router = DefaultRouter()
router.register(r'students', StudentViewSet)
router.register(r'student-marks', StudentMarksViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/student-marks/submit_grades/', submit_grades, name='submit_grades'),
]