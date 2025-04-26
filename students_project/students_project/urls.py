from urllib import request
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
path('admin/', admin.site.urls),
    # Include your existing URLs
    path('', include('students_app.urls')),  # Existing student app URLs
    # Include your existing URLs
    path('', include('grading_system.urls')),
    path('api/reports/', include('pdf_reports.urls', namespace='pdf_reports')),
    path('api/', include('login.urls')),
]

