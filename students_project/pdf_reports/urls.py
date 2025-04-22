# pdf_reports/urls.py
from django.urls import path
from . import views

app_name = 'pdf_reports'

urlpatterns = [
    # Web URLs
    path('results/all/', views.download_all_results, name='download_all_results'),
    path('results/class/<str:class_name>/', views.download_class_results, name='download_class_results'),
    path('results/student/<int:student_id>/', views.download_student_results, name='download_student_results'),
    path('report/<int:report_id>/', views.download_saved_report, name='download_saved_report'),

    # API URLs
    path('api/reports/', views.api_get_reports, name='api_get_reports'),
    path('api/report/<int:report_id>/', views.api_download_report, name='api_download_report'),
]