# views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from django.shortcuts import get_object_or_404
from .models import Student, StudentMarks
from .serializers import StudentSerializer, StudentMarksSerializer, StudentMarksCreateSerializer, \
    BatchMarksSubmissionSerializer
from rest_framework.exceptions import ValidationError


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class StudentMarksViewSet(viewsets.ModelViewSet):
    queryset = StudentMarks.objects.all()
    serializer_class = StudentMarksSerializer

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'update':
            return StudentMarksCreateSerializer
        return StudentMarksSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def submit_grades(self, request):
        """
        Submit grades for multiple students at once
        Expected format:
        [
            {
                "id": 1,
                "total_marks": 450,
                "subject_marks": {
                    "Math": 90,
                    "Eng": 85,
                    "Kis": 75,
                    "Sci": 95,
                    "SST": 80
                }
            },
            ...
        ]
        """
        if not isinstance(request.data, list):
            return Response(
                {"detail": "Expected a list of student marks"},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_marks = []
        errors = []

        for student_data in request.data:
            serializer = StudentMarksCreateSerializer(data=student_data)
            try:
                if serializer.is_valid():
                    marks = serializer.save()
                    created_marks.append(marks.id)
                else:
                    errors.append({
                        'student_id': student_data.get('id'),
                        'error': serializer.errors
                    })
            except ValidationError as e:
                errors.append({
                    'student_id': student_data.get('id'),
                    'error': str(e)
                })

        # If there were errors, include them in the response
        response_data = {}
        if created_marks:
            # Return the created marks
            submitted_marks = StudentMarks.objects.filter(id__in=created_marks)
            marks_serializer = StudentMarksSerializer(submitted_marks, many=True)
            response_data['submitted'] = marks_serializer.data

        if errors:
            response_data['errors'] = errors

        # Return 201 if at least some marks were created, 400 if all failed
        if created_marks:
            return Response(
                response_data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                response_data,
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def get_by_student(self, request):
        """Get marks for a specific student"""
        id = request.query_params.get('id')
        if not id:
            return Response(
                {"detail": "id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        marks = StudentMarks.objects.filter(id=id)
        serializer = StudentMarksSerializer(marks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def get_by_class(self, request):
        """Get marks for all students in a specific class"""
        class_name = request.query_params.get('class_name')
        if not class_name:
            return Response(
                {"detail": "class_name parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find all students in this class
        students = Student.objects.filter(class_name=class_name)
        student_ids = students.values_list('id', flat=True)

        # Get their marks
        marks = StudentMarks.objects.filter(student_id__in=student_ids)
        serializer = StudentMarksSerializer(marks, many=True)
        return Response(serializer.data)


@api_view(['POST'])
def submit_grades(request):
    try:
        serializer = BatchMarksSubmissionSerializer(data=request.data)

        if serializer.is_valid():
            results = serializer.save()
            return Response(
                {"message": f"Grades submitted successfully for {len(results)} students"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except ValidationError as e:
        return Response({"errors": e.detail}, status=status.HTTP_400_BAD_REQUEST)