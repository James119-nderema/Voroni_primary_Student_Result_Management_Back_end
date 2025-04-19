from django.contrib import admin
from django.urls import path, include
from marks_app.views import StudentMarksAPIView

urlpatterns = [

    path('api/student-marks/', StudentMarksAPIView.as_view(), name='student-marks'),
    path('admin/', admin.site.urls),


]


