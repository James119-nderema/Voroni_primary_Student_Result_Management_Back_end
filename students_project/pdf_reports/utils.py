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


def process_student_marks(student, marks_queryset):
    """Process marks for a single student from StudentMarks model with separate subject fields."""
    marks = marks_queryset.first()  # Assuming one result per student
    if not marks:
        return {
            'student_name': f"{student.first_name} {student.last_name}",
            'math_marks': 0, 'math_grade': '(E)',
            'english_marks': 0, 'english_grade': '(E)',
            'kiswahili_marks': 0, 'kiswahili_grade': '(E)',
            'science_marks': 0, 'science_grade': '(E)',
            'sst_marks': 0, 'sst_grade': '(E)',
            'average': 0.0, 'avg_grade': '(E)',
            'total_marks': 0,
        }

    # Map internal fields to printable subject names
    english = marks.eng
    kiswahili = marks.kis
    math = marks.math
    science = marks.sci
    sst = marks.sst

    total = math + english + kiswahili + science + sst
    average = total / 5

    return {
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