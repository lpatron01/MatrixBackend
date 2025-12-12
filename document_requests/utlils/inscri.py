from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from arabic_reshaper import arabic_reshaper
from bidi.algorithm import get_display
import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class KairouanTarsimCertificateGenerator:
    TEXTS = {
        'ar': {
            'header_lines': [
                "الجمهورية التونسية",
                "وزارة التعليم العالي والبحث العلمي",
                "جامعة القيروان",
            ],
            'institute': "المعهد العالي للعلوم التطبيقية والتكنولوجيا بالقيروان",
            'main_title': "شهادة ترسيم",
            'opening': "يشهد الكاتب العام لـ المعهد العالي للعلوم التطبيقية والتكنولوجيا بالقيروان أن الطالب :",
            'name_label': "الاسم :",
            'surname_label': "اللقب :",
            'birth_label': "المولود في :",
            'id_label': "صاحب بطاقة التعريف الوطنية رقم :",
            'year_label': "مرسم بالسنة :",
            'cert_label': "الشهادة :",
            'spec_label': "الاختصاص :",
            'reg_label': "تحت رقم :",
            'closing': "وذلك بالنسبة إلى السنة الجامعية الحالية.",
            'location': "القيروان في",
            'signature_title': "الكاتب العام",
            'footer_notice': "هام : لا تسلم هذه الشهادة الا مرة واحدة",
            'contact1': "شارع بيت الحكمة – 3100 القيروان",
            'contact2': "الهاتف : 73683100  الفاكس : 77235333",
            'contact3': "العنوان الإلكتروني : www.issatkr.rnu.tn",
        },
        'fr': {
            'header_lines': [
                "République Tunisienne",
                "Ministère de l'Enseignement Supérieur et de la Recherche Scientifique",
                "Université de Kairouan",
            ],
            'institute': "Institut Supérieur des Sciences Appliquées et de Technologie de Kairouan",
            'main_title': "Attestation d'Inscription",
            'opening': "Le Secrétaire Général de l'Institut Supérieur des Sciences Appliquées et de Technologie de Kairouan certifie que l'étudiant(e):",
            'name_label': "Prénom :",
            'surname_label': "Nom :",
            'birth_label': "Né(e) le :",
            'id_label': "Titulaire de la carte d'identité nationale n° :",
            'year_label': "Inscrit(e) en année :",
            'cert_label': "Diplôme :",
            'spec_label': "Spécialité :",
            'reg_label': "Sous le numéro :",
            'closing': "Et ce, pour l'année universitaire en cours.",
            'location': "Kairouan, le",
            'signature_title': "Le Secrétaire Général",
            'footer_notice': "Important : Ce certificat n'est délivré qu'une seule fois",
            'contact1': "Rue Bayt El Hikma – 3100 Kairouan",
            'contact2': "Tél : 73683100  Fax : 77235333",
            'contact3': "Adresse électronique : www.issatkr.rnu.tn",
            'fr_opening_title': "Le Secrétaire Général de l'Institut Supérieur des Sciences Appliquées",
            'fr_opening_institute': " et de Technologie de Kairouan certifie que l'étudiant(e):",
        }
    }

    def __init__(self, font_path='arial.ttf', bold_font_path=None, alanguage='ar'):
        """
        Initialize the certificate generator
        font_path: Path to an Arabic-compatible font (e.g., Arial, Amiri, Scheherazade)
        bold_font_path: Path to bold version of the font (optional)
        """
        # Construct paths for fonts using BASE_DIR (same as demande.py)
        absolute_font_path = os.path.join(settings.BASE_DIR, 'document_requests', 'fonts', font_path)
        absolute_bold_font_path = None
        if bold_font_path:
            absolute_bold_font_path = os.path.join(settings.BASE_DIR, 'document_requests', 'fonts', bold_font_path)

        # Register Arabic font
        if os.path.exists(absolute_font_path):
            pdfmetrics.registerFont(TTFont('Arabic', absolute_font_path))
            self.has_font = True
            logger.info(f"Font loaded successfully: {absolute_font_path}")
            
            # Register bold font if available
            if absolute_bold_font_path and os.path.exists(absolute_bold_font_path):
                pdfmetrics.registerFont(TTFont('ArabicBold', absolute_bold_font_path))
                self.has_bold_font = True
                logger.info(f"Bold font loaded successfully: {absolute_bold_font_path}")
            else:
                self.has_bold_font = False
        else:
            logger.error(f"ERROR: Font file '{absolute_font_path}' not found! Please ensure 'Amiri-Regular.ttf' and 'Amiri-Bold.ttf' (or other specified fonts) are in the 'backend/document_requests/fonts/' directory.")
            self.has_font = False
            self.has_bold_font = False
    
    def reshape_arabic(self, text, alanguage='ar'):
        """Reshape and reorder Arabic text for proper display"""
        if alanguage == 'ar':
            try:
                reshaped = arabic_reshaper.reshape(text)
                bidi_text = get_display(reshaped)
                return bidi_text
            except Exception as e:
                logger.error(f"Error reshaping text: {e}")
                return text
        else:
            return text
    
    def draw_text_label_normal_value_bold(self, c, label, value, y_pos, font_size=14, x_margin=80, alanguage='ar'):
        """Draw text with NORMAL label and BOLD value (Arabic RTL order)"""
        width, _ = A4
        font_normal = 'Arabic' if self.has_font else 'Helvetica'
        font_bold = 'ArabicBold' if self.has_bold_font else 'Arabic'
        
        if alanguage == 'fr':
            # LTR: label (normal) left then value (bold) right after
            c.setFont(font_normal, font_size)
            label_width = c.stringWidth(label, font_normal, font_size)
            x_pos = x_margin
            c.drawString(x_pos, y_pos, label)
            c.setFont(font_bold, font_size)
            c.drawString(x_pos + label_width + 5, y_pos, value)
            if not self.has_bold_font:
                c.drawString(x_pos + label_width + 5 + 0.5, y_pos, value)  # Simulate bold
            return x_pos
        else:
            # For Arabic RTL: VALUE (bold) + SPACE + LABEL (normal)
            # This will display as: LABEL VALUE when rendered RTL
            
            # Reshape value (bold)
            value_shaped = self.reshape_arabic(value)
            c.setFont(font_bold, font_size)
            value_width = c.stringWidth(value_shaped, font_bold, font_size)
            
            # Reshape label (normal)
            label_shaped = self.reshape_arabic(label)
            c.setFont(font_normal, font_size)
            label_width = c.stringWidth(label_shaped, font_normal, font_size)
            
            # Calculate total width and starting position (right-aligned)
            total_width = value_width + label_width + 10  # 10 pixels space between label and value
            x_pos = width - x_margin - total_width
            
            # Draw value first (bold) - on the right in RTL
            c.setFont(font_bold, font_size)
            c.drawString(x_pos, y_pos, value_shaped)
            if not self.has_bold_font:
                c.drawString(x_pos + 0.5, y_pos, value_shaped)  # Simulate bold
            
            # Draw label after (normal) - on the left in RTL
            c.setFont(font_normal, font_size)
            c.drawString(x_pos + value_width + 10, y_pos, label_shaped)
            
            return x_pos
    
    def draw_right_text(self, c, text, y_pos, font_size, x_margin=80, is_bold=False):
        """Draw right-aligned text"""
        width, _ = A4
        font_name = 'Arabic' if self.has_font else 'Helvetica'
        
        if is_bold:
            font_name = 'ArabicBold' if self.has_bold_font else font_name
        
        c.setFont(font_name, font_size)
        text_width = c.stringWidth(text, font_name, font_size)
        x_pos = width - x_margin - text_width
        c.drawString(x_pos, y_pos, text)
        
        if is_bold and not self.has_bold_font:
            # Simulate bold
            c.drawString(x_pos + 0.5, y_pos, text)
        
        return x_pos
    
    def draw_left_text(self, c, text, y_pos, font_size, x_margin=80, is_bold=False):
        """Draw left-aligned text"""
        font_name = 'Arabic' if self.has_font else 'Helvetica'
        
        if is_bold:
            font_name = 'ArabicBold' if self.has_bold_font else font_name
        
        c.setFont(font_name, font_size)
        c.drawString(x_margin, y_pos, text)
        
        if is_bold and not self.has_bold_font:
            c.drawString(x_margin + 0.5, y_pos, text)
    
    def draw_left_text_wrapped(self, c, text, y_pos, font_size, x_margin=80, max_width=None, is_bold=False):
        """Draw left-aligned text, wrapping onto multiple lines if it exceeds max_width."""
        width, _ = A4
        if max_width is None:
            max_width = width - 2 * x_margin
        font_name = 'Arabic' if self.has_font else 'Helvetica'
        if is_bold:
            font_name = 'ArabicBold' if self.has_bold_font else font_name
        c.setFont(font_name, font_size)

        words = text.split()
        cur_line = ''
        lines = []
        for word in words:
            test_line = cur_line + ' ' + word if cur_line else word
            test_width = c.stringWidth(test_line, font_name, font_size)
            if test_width <= max_width:
                cur_line = test_line
            else:
                if cur_line:
                    lines.append(cur_line)
                cur_line = word
        if cur_line:
            lines.append(cur_line)

        for line in lines:
            c.drawString(x_margin, y_pos, line.strip())
            y_pos -= font_size + 2
        return y_pos
    
    def draw_centered_text(self, c, text, y_pos, font_size, is_bold=False):
        """Draw centered text"""
        width, _ = A4
        font_name = 'Arabic' if self.has_font else 'Helvetica'
        
        if is_bold:
            font_name = 'ArabicBold' if self.has_bold_font else font_name
        
        c.setFont(font_name, font_size)
        text_width = c.stringWidth(text, font_name, font_size)
        x_pos = (width - text_width) / 2
        c.drawString(x_pos, y_pos, text)
        
        if is_bold and not self.has_bold_font:
            c.drawString(x_pos + 0.5, y_pos, text)
    
    def generate_certificate(self, output_path, alanguage='ar', **params):
        """
        Generate شهادة ترسيم certificate PDF - EXACT COPY of the image structure
        Parameters: name, surname, birth_date, birth_place, national_id,
        year_class, registration_code, certificate_type, specialization, 
        registration_number, year, issue_date, signature_name
        
        ALL PARAMETER VALUES ARE DISPLAYED IN BOLD (labels in normal)
        """
        
        if not self.has_font:
            logger.error("Cannot generate certificate without Arabic font!")
            return
        
        # Create PDF - FULL A4 size
        page_width, page_height = A4
        
        c = canvas.Canvas(output_path, pagesize=A4)
        
        t = self.TEXTS[alanguage]
        # HEADER - Top Right Corner (small text) - LIKE FIRST REFERENCE CODE
        y_pos = page_height - 60
        header_size = 12
        x_margin_header = 60
        
        for line in t['header_lines']:
            text = self.reshape_arabic(line, alanguage)
            if alanguage == 'ar':
                self.draw_right_text(c, text, y_pos, header_size, x_margin=x_margin_header)
            else:
                self.draw_left_text(c, text, y_pos, header_size, x_margin=x_margin_header)
            y_pos -= 20
        
        # المعهد العالي للعلوم التطبيقية والتكنولوجيا بالقيروان - CENTERED
        y_pos -= 15
        institute_text = self.reshape_arabic(t['institute'], alanguage)
        self.draw_centered_text(c, institute_text, y_pos, 14, is_bold=False)
        
        # MAIN TITLE - شهادة ترسيم
        y_pos -= 50
        main_title = self.reshape_arabic(t['main_title'], alanguage)
        self.draw_centered_text(c, main_title, y_pos, 28, is_bold=True)
        
        # Year
        y_pos -= 45
        year_text = params.get('year', '2024 - 2025')
        self.draw_centered_text(c, year_text, y_pos, 18, is_bold=True)
        
        # BODY - Right aligned with VALUES IN BOLD
        y_pos -= 65
        body_font_size = 14
        x_margin = 80
        
        # Opening line - RIGHT ALIGNED (normal)
        opening = self.reshape_arabic(t['opening'], alanguage)
        if alanguage == 'ar':
            self.draw_right_text(c, opening, y_pos, body_font_size, x_margin, is_bold=False)
        else:
            # French opening statement needs to be split and left-aligned with wrapping
            self.draw_left_text_wrapped(c, t['fr_opening_title'], y_pos, body_font_size, x_margin, is_bold=False)
            y_pos -= body_font_size + 2 # Adjust y_pos for the line drawn by draw_left_text_wrapped
            self.draw_left_text_wrapped(c, t['fr_opening_institute'], y_pos, body_font_size, x_margin, is_bold=False)
            y_pos -= body_font_size + 2 # Adjust y_pos for the line drawn by draw_left_text_wrapped
        
        # Student information - LABELS NORMAL, VALUES BOLD (right-aligned)
        y_pos -= 35
        name_label = t['name_label']
        name_value = params.get('name', 'أحمد خليل' if alanguage=='ar' else 'Ahmed Khalil')
        self.draw_text_label_normal_value_bold(c, name_label, name_value, y_pos, body_font_size, x_margin, alanguage)
        
        y_pos -= 35
        surname_label = t['surname_label']
        surname_value = params.get('surname', 'ورشي' if alanguage=='ar' else 'Ouergui')
        self.draw_text_label_normal_value_bold(c, surname_label, surname_value, y_pos, body_font_size, x_margin, alanguage)
        
        y_pos -= 35
        birth_label = t['birth_label']
        if alanguage == 'ar':
            birth_value = f"{params.get('birth_date', '2004/01/28')}  بـ : {params.get('birth_place', 'ساقية سيدي يوسف')}"
        else:
            birth_value = f"{params.get('birth_date', '28/01/2004')} à : {params.get('birth_place', 'Sakiet Sidi Youssef')}"
        self.draw_text_label_normal_value_bold(c, birth_label, birth_value, y_pos, body_font_size, x_margin, alanguage)
        
        y_pos -= 35
        id_label = t['id_label']
        id_value = params.get('national_id', '14440542')
        self.draw_text_label_normal_value_bold(c, id_label, id_value, y_pos, body_font_size, x_margin, alanguage)
        
        y_pos -= 35
        year_label = t['year_label']
        if alanguage == 'ar':
            year_value = f"{params.get('year_class', 'الثالثة')} , فوج : {params.get('registration_code', 'GLSI3 A')}"
        else:
            year_value = f"{params.get('year_class', 'Troisième')} , Groupe : {params.get('registration_code', 'GLSI3 A')}"
        self.draw_text_label_normal_value_bold(c, year_label, year_value, y_pos, body_font_size, x_margin, alanguage)
        
        y_pos -= 35
        cert_label = t['cert_label']
        cert_value = params.get('certificate_type', 'الإجازة في علوم الإعلامية' if alanguage=='ar' else "Licence en Informatique")
        self.draw_text_label_normal_value_bold(c, cert_label, cert_value, y_pos, body_font_size, x_margin, alanguage)
        
        y_pos -= 35
        spec_label = t['spec_label']
        spec_value = params.get('specialization', 'هندسة البرمجيات ونظم المعلومات' if alanguage=='ar' else "Génie Logiciel et Systèmes d'Information")
        self.draw_text_label_normal_value_bold(c, spec_label, spec_value, y_pos, body_font_size, x_margin, alanguage)
        
        y_pos -= 35
        reg_label = t['reg_label']
        reg_value = params.get('registration_number', '22003013')
        self.draw_text_label_normal_value_bold(c, reg_label, reg_value, y_pos, body_font_size, x_margin, alanguage)
        
        y_pos -= 35
        closing = self.reshape_arabic(t['closing'], alanguage)
        if alanguage == 'ar':
            self.draw_right_text(c, closing, y_pos, body_font_size, x_margin, is_bold=False)
        else:
            self.draw_left_text(c, closing, y_pos, body_font_size, x_margin, is_bold=False)
        
        # Date and signature - LEFT ALIGNED
        y_pos -= 45
        
        # FIXED: Use the same method as in the reference code
        # Draw complete text: "القيروان في 2024/09/18"
        location_text = t['location']
        issue_date = params.get('issue_date', '2024/09/18' if alanguage=='ar' else '18/09/2024')
        location_full = f"{location_text} {issue_date}"
        location_shaped = self.reshape_arabic(location_full, alanguage)
        self.draw_left_text(c, location_shaped, y_pos, 14, x_margin=60, is_bold=False)
        
        y_pos -= 30
        signature_title = self.reshape_arabic(t['signature_title'], alanguage)
        self.draw_left_text(c, signature_title, y_pos, 14, x_margin=60, is_bold=False)
        
        # Add space after signature title to prevent overlap with footer notice
        y_pos -= 30 # Increased spacing to account for footer notice
        
        # FOOTER - Bottom Right Corner - LIKE FIRST REFERENCE CODE
        # Removed fixed y_pos = 120 to prevent overlap
        
        # Important notice (right aligned)
        footer_notice = self.reshape_arabic(t['footer_notice'], alanguage)
        if alanguage == 'ar':
            self.draw_right_text(c, footer_notice, y_pos, 12, x_margin=60, is_bold=True)
        else:
            self.draw_left_text_wrapped(c, footer_notice, y_pos, 12, x_margin=60, is_bold=True)
        
        # Horizontal line
        y_pos -= 15
        c.setStrokeColor(HexColor('#000000'))
        c.line(60, y_pos, page_width - 60, y_pos)
        
        # Contact information (right aligned, smaller)
        y_pos -= 20
        contact1 = self.reshape_arabic(t['contact1'], alanguage)
        if alanguage == 'ar':
            self.draw_right_text(c, contact1, y_pos, 10, x_margin=60)
        else:
            self.draw_left_text_wrapped(c, contact1, y_pos, 10, x_margin=60)
        
        y_pos -= 18
        contact2 = self.reshape_arabic(t['contact2'], alanguage)
        if alanguage == 'ar':
            self.draw_right_text(c, contact2, y_pos, 10, x_margin=60)
        else:
            self.draw_left_text_wrapped(c, contact2, y_pos, 10, x_margin=60)
        
        y_pos -= 18
        contact3 = self.reshape_arabic(t['contact3'], alanguage)
        if alanguage == 'ar':
            self.draw_right_text(c, contact3, y_pos, 10, x_margin=60)
        else:
            self.draw_left_text_wrapped(c, contact3, y_pos, 10, x_margin=60)
        
        # Save PDF
        c.save()
        logger.info(f"✓ Certificate generated successfully: {output_path}")
        logger.info(f"  Type: {t['main_title']} ({'Registration Certificate' if alanguage=='fr' else 'شهادة ترسيم'})")
        logger.info(f"  Layout: Values in BOLD, labels in normal")
        logger.info(f"  Header/Footer: {'Left' if alanguage=='fr' else 'Right'} Corner")
        logger.info(f"  Date format: '{location_full}' (place then date)")
        return True