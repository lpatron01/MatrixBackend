from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from django.conf import settings
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from arabic_reshaper import arabic_reshaper
from bidi.algorithm import get_display

def generate_document_request_pdf(document_request):
    file_name = f"demande_{document_request.public_id}.pdf"
    file_path = os.path.join(settings.MEDIA_ROOT, 'document_requests/pdfs/', file_name)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Arabic Text Configuration and Helpers
    TEXTS = {
        'ar': {
            'header_lines': [
                "الجمهورية التونسية",
                "وزارة التعليم العالي والبحث العلمي",
                "جامعة القيروان",
            ],
            'institute': "المعهد العالي للعلوم التطبيقية والتكنولوجيا بالقيروان",
            'main_title': "مطلب وثيقة",
            'student_info': "معلومات الطالب:",
            'name_label': "الاسم واللقب:",
            'cin_label': "رقم بطاقة التعريف الوطنية:",
            'email_label': "البريد الإلكتروني:",
            'request_details': "تفاصيل المطلب:",
            'document_type_label': "نوع الوثيقة:",
            'language_label': "اللغة:",
            'reception_type_label': "طريقة الاستلام:",
            'created_at_label': "تاريخ الإنشاء:",
            'footer_notice': "هام : هذا المطلب صالح للاستعمال مرة واحدة فقط",
            'contact1': "شارع بيت الحكمة – 3100 القيروان",
            'contact2': "الهاتف : 73683100  الفاكس : 77235333",
            'contact3': "العنوان الإلكتروني : www.issatkr.rnu.tn",
            'location': "القيروان في",
            'signature_title': "الإمضاء",
        }
    }

    def reshape_arabic(text):
        try:
            reshaped = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped)
            return bidi_text
        except Exception as e:
            print(f"Error reshaping text: {e}")
            return text

    # Font loading logic
    font_paths = [
        os.path.join(settings.BASE_DIR, 'document_requests', 'fonts', 'Amiri-Regular.ttf'),
    ]
    bold_font_paths = [
        os.path.join(settings.BASE_DIR, 'document_requests', 'fonts', 'Amiri-Bold.ttf'),
    ]

    font_file = None
    bold_font_file = None

    for font in font_paths:
        if os.path.exists(font):
            font_file = font
            break

    for bold_font in bold_font_paths:
        if os.path.exists(bold_font):
            bold_font_file = bold_font
            break

    has_font = False
    has_bold_font = False

    if font_file:
        pdfmetrics.registerFont(TTFont('Arabic', font_file))
        has_font = True
        if bold_font_file:
            pdfmetrics.registerFont(TTFont('ArabicBold', bold_font_file))
            has_bold_font = True
    else:
        print("ERROR: No Arabic font found! Using Helvetica.")

    # Helper drawing functions adapted from i.py
    def draw_right_text(canvas_obj, text, y_pos, font_size, x_margin=60, is_bold=False):
        width, _ = A4
        font_name = 'Arabic' if has_font else 'Helvetica'
        if is_bold:
            font_name = 'ArabicBold' if has_bold_font else font_name
        canvas_obj.setFont(font_name, font_size)
        text_width = canvas_obj.stringWidth(text, font_name, font_size)
        x_pos = width - x_margin - text_width
        canvas_obj.drawString(x_pos, y_pos, text)
        if is_bold and not has_bold_font:
            canvas_obj.drawString(x_pos + 0.5, y_pos, text) # Simulate bold

    def draw_left_text(canvas_obj, text, y_pos, font_size, x_margin=60, is_bold=False):
        font_name = 'Arabic' if has_font else 'Helvetica'
        if is_bold:
            font_name = 'ArabicBold' if has_bold_font else font_name
        canvas_obj.setFont(font_name, font_size)
        canvas_obj.drawString(x_margin, y_pos, text)
        if is_bold and not has_bold_font:
            canvas_obj.drawString(x_margin + 0.5, y_pos, text) # Simulate bold

    def draw_centered_text(canvas_obj, text, y_pos, font_size, is_bold=False):
        width, _ = A4
        font_name = 'Arabic' if has_font else 'Helvetica'
        if is_bold:
            font_name = 'ArabicBold' if has_bold_font else font_name
        canvas_obj.setFont(font_name, font_size)
        text_width = canvas_obj.stringWidth(text, font_name, font_size)
        x_pos = (width - text_width) / 2
        canvas_obj.drawString(x_pos, y_pos, text)
        if is_bold and not has_bold_font:
            canvas_obj.drawString(x_pos + 0.5, y_pos, text) # Simulate bold

    def draw_text_label_normal_value_bold(canvas_obj, label, value, y_pos, font_size=14, x_margin=60):
        width, _ = A4
        font_normal = 'Arabic' if has_font else 'Helvetica'
        font_bold = 'ArabicBold' if has_bold_font else 'Arabic'

        value_shaped = reshape_arabic(value)
        canvas_obj.setFont(font_bold, font_size)
        value_width = canvas_obj.stringWidth(value_shaped, font_bold, font_size)

        label_shaped = reshape_arabic(label)
        canvas_obj.setFont(font_normal, font_size)
        label_width = canvas_obj.stringWidth(label_shaped, font_normal, font_size)

        total_width = value_width + label_width + 10
        x_pos = width - x_margin - total_width

        canvas_obj.setFont(font_bold, font_size)
        canvas_obj.drawString(x_pos, y_pos, value_shaped)
        if not has_bold_font:
            canvas_obj.drawString(x_pos + 0.5, y_pos, value_shaped) # Simulate bold

        canvas_obj.setFont(font_normal, font_size)
        canvas_obj.drawString(x_pos + value_width + 10, y_pos, label_shaped)

    def draw_left_text_wrapped(canvas_obj, text, y_pos, font_size, x_margin=60, max_width=None, is_bold=False):
        width, _ = A4
        if max_width is None:
            max_width = width - 2 * x_margin
        font_name = 'Arabic' if has_font else 'Helvetica'
        if is_bold:
            font_name = 'ArabicBold' if has_bold_font else font_name
        canvas_obj.setFont(font_name, font_size)

        words = text.split()
        cur_line = ''
        lines = []
        for word in words:
            test_line = cur_line + ' ' + word if cur_line else word
            test_width = canvas_obj.stringWidth(test_line, font_name, font_size)
            if test_width <= max_width:
                cur_line = test_line
            else:
                if cur_line:
                    lines.append(cur_line)
                cur_line = word
        if cur_line:
            lines.append(cur_line)

        for line in lines:
            canvas_obj.drawString(x_margin, y_pos, line.strip())
            y_pos -= font_size + 2
        return y_pos

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    t = TEXTS['ar']

    # Header
    y_pos = height - 60
    header_size = 12
    x_margin_header = 60

    for line in t['header_lines']:
        text = reshape_arabic(line)
        draw_right_text(c, text, y_pos, header_size, x_margin=x_margin_header)
        y_pos -= 20

    y_pos -= 15
    institute_text = reshape_arabic(t['institute'])
    draw_centered_text(c, institute_text, y_pos, 14, is_bold=False)

    y_pos -= 60  # Adjusted from 50 for more space
    main_title = reshape_arabic(t['main_title'])
    draw_centered_text(c, main_title, y_pos, 28, is_bold=True)

    y_pos -= 60  # Adjusted from 50 for more space
    body_font_size = 14
    x_margin = 60

    # Student Information
    y_pos -= 35
    draw_right_text(c, reshape_arabic(t['student_info']), y_pos, 16, x_margin, is_bold=True) # Increased font size to 16
    y_pos -= 28  # Adjusted for increased spacing after subtitle
    draw_text_label_normal_value_bold(c, t['name_label'], f"{document_request.student.first_name} {document_request.student.last_name}", y_pos, body_font_size, x_margin)
    y_pos -= 25  # Increased line spacing
    draw_text_label_normal_value_bold(c, t['cin_label'], document_request.student.cin if document_request.student.cin else 'N/A', y_pos, body_font_size, x_margin)
    y_pos -= 25  # Increased line spacing
    draw_text_label_normal_value_bold(c, t['email_label'], document_request.student.email, y_pos, body_font_size, x_margin)

    # Document Request Information
    y_pos -= 40
    draw_right_text(c, reshape_arabic(t['request_details']), y_pos, 16, x_margin, is_bold=True) # Increased font size to 16
    y_pos -= 28  # Adjusted for increased spacing after subtitle
    draw_text_label_normal_value_bold(c, t['document_type_label'], document_request.get_document_type_display(), y_pos, body_font_size, x_margin)
    y_pos -= 25  # Increased line spacing
    draw_text_label_normal_value_bold(c, t['language_label'], document_request.get_language_display(), y_pos, body_font_size, x_margin)
    y_pos -= 25  # Increased line spacing
    draw_text_label_normal_value_bold(c, t['reception_type_label'], document_request.get_reception_type_display(), y_pos, body_font_size, x_margin)
    y_pos -= 25  # Increased line spacing
    draw_text_label_normal_value_bold(c, t['created_at_label'], document_request.created_at.strftime('%Y-%m-%d %H:%M'), y_pos, body_font_size, x_margin)

    # Footer
    # Calculate footer starting position to be at the bottom of the page
    footer_bottom_margin = 40
    footer_line_height = 18 # Approximate height for contact lines
    footer_notice_height = 15 # For the important notice
    horizontal_line_height = 15
    signature_title_height = 14 + 30 # Font size + space after
    location_full_height = 14 + 30 # Font size + space after

    # Total estimated footer height
    total_footer_height = (
        3 * footer_line_height +  # 3 contact lines
        horizontal_line_height +  # horizontal line
        footer_notice_height +    # footer notice
        signature_title_height +  # signature title
        location_full_height     # location and date
    )

    y_pos_footer_start = footer_bottom_margin + total_footer_height

    # Adjust y_pos to start drawing footer from the bottom up
    y_pos = y_pos_footer_start

    # Contact information (right aligned, smaller)
    contact3 = reshape_arabic(t['contact3'])
    draw_right_text(c, contact3, footer_bottom_margin + 18*0, 10, x_margin=60)
    contact2 = reshape_arabic(t['contact2'])
    draw_right_text(c, contact2, footer_bottom_margin + 18*1, 10, x_margin=60)
    contact1 = reshape_arabic(t['contact1'])
    draw_right_text(c, contact1, footer_bottom_margin + 18*2, 10, x_margin=60)

    # Horizontal line
    c.setStrokeColor(HexColor('#000000'))
    c.line(60, footer_bottom_margin + 18*3 + 5, width - 60, footer_bottom_margin + 18*3 + 5)



    # Date and signature - LEFT ALIGNED (positioned above footer notice)
    issue_date = document_request.created_at.strftime('%Y/%m/%d')
    location_full = f"{t['location']} {issue_date}"
    draw_left_text(c, reshape_arabic(location_full), footer_bottom_margin + 18*3 + 15 + 30, 14, x_margin=60, is_bold=False)

    signature_title = reshape_arabic(t['signature_title'])
    draw_left_text(c, signature_title, footer_bottom_margin + 18*3 + 15 + 30 + 30, 14, x_margin=60, is_bold=False)

    c.save()
    return file_path
