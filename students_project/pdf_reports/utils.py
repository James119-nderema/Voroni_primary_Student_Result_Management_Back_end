# pdf_reports/utils.py
from io import BytesIO
import os
from datetime import datetime
from django.template.loader import get_template
from django.conf import settings
from xhtml2pdf import pisa
from django.core.files.storage import FileSystemStorage
from django.db.models import Sum, Avg


def calculate_grade(marks):
    """Calculate grade based on marks"""
    if marks >= 70:
        return 'E.E'
    elif marks >= 60:
        return 'M.E'
    elif marks >= 40:
        return 'A.E'
    else:
        return 'B.E'


def process_student_marks(students, marks_queryset):
    """Process marks for all students with position ranking based on total marks."""
    student_results = []

    # First, gather all student data
    for student in students:
        # Use student_id instead of student to match the model field
        marks = marks_queryset.filter(student_id=student.id).first()  # Assuming one result per student
        if not marks:
            student_result = {
                'student_name': f"{student.first_name} {student.last_name}",
                'math_marks': 0, 'math_grade': '(E)',
                'english_marks': 0, 'english_grade': '(E)',
                'kiswahili_marks': 0, 'kiswahili_grade': '(E)',
                'science_marks': 0, 'science_grade': '(E)',
                'sst_marks': 0, 'sst_grade': '(E)',
                'average': 0.0, 'avg_grade': '(E)',
                'total_marks': 0,
            }
        else:
            # Map internal fields to printable subject names
            english = marks.eng
            kiswahili = marks.kis
            math = marks.math
            science = marks.sci
            sst = marks.sst

            total = math + english + kiswahili + science + sst
            average = total / 5

            student_result = {
                'student_name': getattr(student, 'full_name', f"{student.first_name} {student.last_name}"),
                'math_marks': math,
                'math_grade': f"{calculate_grade(math)}",
                'english_marks': english,
                'english_grade': f"{calculate_grade(english)}",
                'kiswahili_marks': kiswahili,
                'kiswahili_grade': f"{calculate_grade(kiswahili)}",
                'science_marks': science,
                'science_grade': f"{calculate_grade(science)}",
                'sst_marks': sst,
                'sst_grade': f"{calculate_grade(sst)}",
                'average': round(average, 2),
                'avg_grade': f"{calculate_grade(average)}",
                'total_marks': total
            }

        student_results.append(student_result)

    # Sort the results by total marks in descending order
    student_results.sort(key=lambda x: x['total_marks'], reverse=True)

    # Assign positions after sorting
    for i, result in enumerate(student_results):
        result['position'] = i + 1  # Positions start from 1

    return student_results


def get_class_results(students_by_class, marks_model):
    """Get results grouped by class with students ranked by position."""
    class_groups = {}

    for class_name, students in students_by_class.items():
        # Use a list of student IDs for filtering
        student_ids = [student.id for student in students]
        # Process all students in this class
        student_results = process_student_marks(students, marks_model.objects.filter(student_id__in=student_ids))
        class_groups[class_name] = student_results

    return class_groups


def render_to_pdf(template_src, context_dict):
    """Render HTML template to PDF"""
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return result
    return None


def save_pdf(pdf_file, filename):
    """Save PDF file to disk"""
    # Create directory for reports if it doesn't exist
    reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
    os.makedirs(reports_dir, exist_ok=True)

    # Save the PDF to disk
    fs = FileSystemStorage(location=reports_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename}_{timestamp}.pdf"
    filename = fs.save(filename, pdf_file)

    return os.path.join('reports', filename)