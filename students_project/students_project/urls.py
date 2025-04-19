
from students_app import views
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
path('admin/', admin.site.urls),
    # Include your existing URLs
    path('', include('students_app.urls')),  # Existing student app URLs
    # Include the new marks app URLs
    path('', include('marks_app.urls')),
    path('admin/', admin.site.urls),
    # Include your existing URLs
    path('', include('students_app.urls')),  # Existing student app URLs
    # Include the new marks app URLs
    path('', include('marks_app.urls')),

]


