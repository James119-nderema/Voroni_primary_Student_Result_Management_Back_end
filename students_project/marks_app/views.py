# marks_app/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import StudentMarks
from .serializers import StudentMarksSerializer


class StudentMarksAPIView(APIView):
    def get(self, request, *args, **kwargs):
        """
        Get a list of all student marks.
        """
        marks = StudentMarks.objects.all()
        serializer = StudentMarksSerializer(marks, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Create new student marks entries.
        """
        # Handle single student mark submission
        if isinstance(request.data, dict):
            serializer = StudentMarksSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Handle bulk submission of student marks
        elif isinstance(request.data, list):
            serializers = []
            for item in request.data:
                serializer = StudentMarksSerializer(data=item)
                if serializer.is_valid():
                    serializer.save()
                    serializers.append(serializer.data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializers, status=status.HTTP_201_CREATED)

        return Response({"error": "Invalid format"}, status=status.HTTP_400_BAD_REQUEST)