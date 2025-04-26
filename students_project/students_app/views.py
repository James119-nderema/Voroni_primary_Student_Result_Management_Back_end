from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from students_app.models import Student
from .serializers import StudentSerializer
from .models import ClassDetails
from .serializers import ClassDetailsSerializer

@api_view(['GET', 'POST'])
def student_list(request):
    """
    List all students or create a new student
    """
    if request.method == 'GET':
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def student_detail(request, pk):
    """
    Retrieve, update or delete a student instance
    """
    try:
        student = Student.objects.get(pk=pk)
    except Student.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = StudentSerializer(student)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = StudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Add these functions to your existing views.py
@api_view(['GET', 'POST'])
def class_list(request):
    """
    List all classes or create a new class
    """
    if request.method == 'GET':
        classes = ClassDetails.objects.all()
        serializer = ClassDetailsSerializer(classes, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ClassDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def class_detail(request, pk):
    """
    Retrieve, update or delete a class by id
    """
    try:
        class_obj = ClassDetails.objects.get(pk=pk)
    except ClassDetails.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ClassDetailsSerializer(class_obj)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ClassDetailsSerializer(class_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        class_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Add a single item API view for Student
@api_view(['POST'])
def add_student(request):
    """
    Add a single student to the database
    """
    if request.method == 'POST':
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Add a single item API view for ClassDetails
@api_view(['POST'])
def add_class(request):
    """
    Add a single class to the database
    """
    if request.method == 'POST':
        serializer = ClassDetailsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def student_count(request):
    """
    Get the total number of students in the database
    """
    count = Student.objects.count()
    return Response({'count': count})