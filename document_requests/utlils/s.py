from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from arabic_reshaper import arabic_reshaper
from bidi.algorithm import get_display
import os

class ArabicCertificateGenerator:
    TEXTS = {
        'ar': {
            'header_lines': [
                "الجمهورية التونسية",
                "وزارة التعليم العالي والبحث العلمي",
                "جامعة القيروان",
            ],
            'institute': "المعهد العالي للعلوم التطبيقية والتكنولوجيا بالقيروان",
            'main_title': "شهادة نجاح",
            'opening': "يشهد الكاتب العام لـ: المعهد العالي للعلوم التطبيقية والتكنولوجيا بالقيروان أن الطالب:",
            'name_label': "الاسم:",
            'surname_label': "اللقب:",
            'birth_label': "المولود في:",
            'id_label': "صاحب بطاقة التعريف الوطنية رقم:",
            'reg_label': "مرسم تحت رقم:",
            'cert_label': "الشهادة:",
            'spec_label': "الاختصاص:",
            'success_text': "بالنسبة للسنة الجامعية {year} قد اجتاز بنجاح امتحانات السنة الثانية",
            'grade_text': "في الدورة الرئيسية بملاحظة {grade}",
            'delivery': "سلمت هذه الشهادة إلى المعني بالأمر للإدلاء بها لدى من له النظر.",
            'location': "القيروان في",
            'signature_title': "الكاتب العام",
            'footer_notice': "هام: لا تسلم هذه الشهادة إلا مرة واحدة",
            'contact1': "شارع بيت الحكمة – 3100 القيروان",
            'contact2': "الهاتف: 73683100  الفاكس: 77235333",
            'contact3': "العنوان الإلكتروني: www.issatkr.rnu.tn",
        },
        'fr': {
            'header_lines': [
                "République Tunisienne",
                "Ministère de l'Enseignement Supérieur et de la Recherche Scientifique",
                "Université de Kairouan",
            ],
            'institute': "Institut Supérieur des Sciences Appliquées et de Technologie de Kairouan",
            'main_title': "Attestation de Réussite",
            'opening': "Le Secrétaire Général de l'Institut Supérieur des Sciences Appliquées et de Technologie de Kairouan atteste que l'étudiant(e):",
            'name_label': "Prénom:",
            'surname_label': "Nom:",
            'birth_label': "Né(e) le:",
            'id_label': "Titulaire de la carte d'identité nationale n°:",
            'reg_label': "Inscrit(e) sous le numéro:",
            'cert_label': "Diplôme:",
            'spec_label': "Spécialité:",
            'success_text': "Pour l'année universitaire {year}, a réussi les examens de la deuxième année avec succès.",
            'grade_text': "à la session principale avec la mention {grade}",
            'delivery': "Le présent certificat est délivré à l'intéressé(e) pour servir et valoir ce que de droit.",
            'location': "Kairouan, le",
            'signature_title': "Le Secrétaire Général",
            'footer_notice': "Important: Ce certificat n'est délivré qu'une seule fois",
            'contact1': "Rue Bayt El Hikma – 3100 Kairouan",
            'contact2': "Tél: 73683100  Fax: 77235333",
            'contact3': "Adresse électronique: www.issatkr.rnu.tn",
            'fr_opening_title': "Le Secrétaire Général de l'Institut Supérieur des Sciences Appliquées",
            'fr_opening_institute': " et de Technologie de Kairouan atteste que l'étudiant(e):",
        }
    }

    def __init__(self, font_path='arial.ttf', bold_font_path=None, alanguage='ar'):
        """
        Initialize the certificate generator
        font_path: Path to an Arabic-compatible font (e.g., Arial, Amiri, Scheherazade)
        bold_font_path: Path to bold version of the font (optional)
        """
        # Register Arabic font
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('Arabic', font_path))
            self.has_font = True
            print(f"Font loaded successfully: {font_path}")
            
            # Register bold font if available
            if bold_font_path and os.path.exists(bold_font_path):
                pdfmetrics.registerFont(TTFont('ArabicBold', bold_font_path))
                self.has_bold_font = True
                print(f"Bold font loaded successfully: {bold_font_path}")
            else:
                self.has_bold_font = False
        else:
            print(f"ERROR: Font file '{font_path}' not found!")
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
                print(f"Error reshaping text: {e}")
                return text
        else:
            return text
    
    def draw_text_label_normal_value_bold(self, c, label, value, y_pos, font_size=14, x_margin=80, alanguage='ar'):
        """Draw label and value for Arabic (RTL) or French (LTR)."""
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
            # RTL (default Arabic logic): value (bold), then label (normal)
            value_shaped = self.reshape_arabic(value)
            c.setFont(font_bold, font_size)
            value_width = c.stringWidth(value_shaped, font_bold, font_size)
            label_shaped = self.reshape_arabic(label)
            c.setFont(font_normal, font_size)
            label_width = c.stringWidth(label_shaped, font_normal, font_size)
            total_width = value_width + label_width + 5
            x_pos = width - x_margin - total_width
            c.setFont(font_bold, font_size)
            c.drawString(x_pos, y_pos, value_shaped)
            if not self.has_bold_font:
                c.drawString(x_pos + 0.5, y_pos, value_shaped)
            c.setFont(font_normal, font_size)
            c.drawString(x_pos + value_width + 5, y_pos, label_shaped)
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

    def generate_certificate(self, output_path, alanguage='ar', **params):
        """
        Generate certificate PDF (FULL A4 PAGE)
        Parameters: name, surname, birth_date, birth_place, national_id,
        registration_number, registration_code, year, certificate_type,
        specialization, grade, issue_date
        ALL PARAMETER VALUES ARE DISPLAYED IN BOLD
        """
        
        if not self.has_font:
            print("Cannot generate certificate without Arabic font!")
            return
        
        # Create PDF - FULL A4 size
        page_width, page_height = A4
        
        c = canvas.Canvas(output_path, pagesize=A4)
        t = self.TEXTS[alanguage]
        
        # HEADER - Top Right Corner (small text)
        y_pos = page_height - 60
        header_size = 11
        x_margin_header = 60
        
        for line in t['header_lines']:
            text = self.reshape_arabic(line, alanguage)
            if alanguage == 'ar':
                self.draw_right_text(c, text, y_pos, header_size, x_margin=x_margin_header)
            else:
                self.draw_left_text(c, text, y_pos, header_size, x_margin=x_margin_header)
            y_pos -= 18
        
        # المعهد العالي للإعلامية بالمهدية - CENTERED (before شهادة نجاح)
        y_pos -= 10
        institute_text = self.reshape_arabic(t['institute'], alanguage)
        self.draw_centered_text(c, institute_text, y_pos, 13, is_bold=False)
        
        # MAIN TITLE - Centered and Large
        y_pos -= 45
        main_title = self.reshape_arabic(t['main_title'], alanguage)
        self.draw_centered_text(c, main_title, y_pos, 28, is_bold=True)
        
        # Year - BOLD
        y_pos -= 40
        year_text = params.get('year', '2023 - 2024')
        self.draw_centered_text(c, year_text, y_pos, 16, is_bold=True)
        
        # BODY - Right aligned with larger font
        y_pos -= 60
        x_margin = 80
        body_font_size = 14
        
        # Opening line
        if alanguage == 'ar':
            opening = self.reshape_arabic(t['opening'], alanguage)
            self.draw_right_text(c, opening, y_pos, body_font_size, x_margin, is_bold=False)
            y_pos -= 32
        else:
            # First line: "Le Secrétaire Général"
            self.draw_left_text_wrapped(c, t['fr_opening_title'], y_pos, body_font_size, x_margin, is_bold=False)
            y_pos -= body_font_size + 2 # Adjust y_pos for the line drawn
            # Second line: "de l'Institut Supérieur ... "
            self.draw_left_text_wrapped(c, t['fr_opening_institute'], y_pos, body_font_size, x_margin, is_bold=False)
            y_pos -= body_font_size + 2 # Adjust y_pos for the line drawn
        
        # Student information - ONLY VALUES IN BOLD (labels normal)
        y_pos -= 32
        name_label = t['name_label']
        name_value = params.get('name', 'أحمد خليل' if alanguage=='ar' else 'Ahmed Khalil')
        self.draw_text_label_normal_value_bold(c, name_label, name_value, y_pos, body_font_size, x_margin, alanguage)
        
        y_pos -= 32
        surname_label = t['surname_label']
        surname_value = params.get('surname', 'ورشي' if alanguage=='ar' else 'Ouergui')
        self.draw_text_label_normal_value_bold(c, surname_label, surname_value, y_pos, body_font_size, x_margin, alanguage)
        
        y_pos -= 32
        birth_label = t['birth_label']
        if alanguage == 'ar':
            birth_value = f"{params.get('birth_date', '2004/01/28')} بـ {params.get('birth_place', 'ساقية سيدي يوسف')}"
        else:
            birth_value = f"{params.get('birth_date', '28/01/2004')} à {params.get('birth_place', 'Sakiet Sidi Youssef')}"
        self.draw_text_label_normal_value_bold(c, birth_label, birth_value, y_pos, body_font_size, x_margin, alanguage)
        
        y_pos -= 32
        id_label = t['id_label']
        id_value = params.get('national_id', '14440542')
        self.draw_text_label_normal_value_bold(c, id_label, id_value, y_pos, body_font_size, x_margin, alanguage)
        
        y_pos -= 32
        reg_label = t['reg_label']
        if alanguage == 'ar':
            reg_value = f"{params.get('registration_number', '22003013')} الفوج : {params.get('registration_code', 'GLSI2B')}"
        else:
            reg_value = f"{params.get('registration_number', '22003013')} Groupe : {params.get('registration_code', 'GLSI2B')}"
        self.draw_text_label_normal_value_bold(c, reg_label, reg_value, y_pos, body_font_size, x_margin, alanguage)
        
        y_pos -= 32
        success = t['success_text'].format(year=params.get('year', '2023 - 2024'))
        success_text = self.reshape_arabic(success, alanguage)
        if alanguage == 'ar':
            self.draw_right_text(c, success_text, y_pos, body_font_size, x_margin, is_bold=False)
        else:
            self.draw_left_text_wrapped(c, success_text, y_pos, body_font_size, x_margin, is_bold=False)
        
        y_pos -= 32
        cert_label = t['cert_label']
        cert_value = params.get('certificate_type', 'الإجازة في علوم الإعلامية' if alanguage=='ar' else 'Licence en Informatique')
        self.draw_text_label_normal_value_bold(c, cert_label, cert_value, y_pos, body_font_size, x_margin, alanguage)
        
        y_pos -= 32
        spec_label = t['spec_label']
        spec_value = params.get('specialization', 'هندسة البرمجيات ونظم المعلومات' if alanguage=='ar' else "Génie Logiciel et Systèmes d'Information")
        self.draw_text_label_normal_value_bold(c, spec_label, spec_value, y_pos, body_font_size, x_margin, alanguage)
        
        y_pos -= 32
        grade = t['grade_text'].format(grade=params.get('grade', 'حسن' if alanguage=='ar' else 'Bien'))
        grade_text = self.reshape_arabic(grade, alanguage)
        if alanguage == 'ar':
            self.draw_right_text(c, grade_text, y_pos, body_font_size, x_margin, is_bold=False)
        else:
            self.draw_left_text_wrapped(c, grade_text, y_pos, body_font_size, x_margin, is_bold=False)
        
        # Delivery statement
        y_pos -= 40
        delivery = self.reshape_arabic(t['delivery'], alanguage)
        if alanguage == 'ar':
            self.draw_right_text(c, delivery, y_pos, 12, x_margin)
        else:
            self.draw_left_text_wrapped(c, delivery, y_pos, 12, x_margin)
        
        # Date and signature - LEFT ALIGNED
        y_pos -= 28
        location_text = t['location']
        issue_date = params.get('issue_date', '2024/06/24' if alanguage=='ar' else '24/06/2024')
        location_full = f"{location_text} {issue_date}"
        location_shaped = self.reshape_arabic(location_full, alanguage)
        self.draw_left_text(c, location_shaped, y_pos, 12, x_margin, is_bold=False)
        
        y_pos -= 25
        signature_title = self.reshape_arabic(t['signature_title'], alanguage)
        self.draw_left_text(c, signature_title, y_pos, 12, x_margin)
        
        # FOOTER - Bottom Right Corner
        y_pos = 120
        
        # Important notice (right aligned)
        footer_notice = self.reshape_arabic(t['footer_notice'], alanguage)
        if alanguage == 'ar':
            self.draw_right_text(c, footer_notice, y_pos, 10, x_margin=60, is_bold=True)
        else:
            self.draw_left_text_wrapped(c, footer_notice, y_pos, 10, x_margin=60, is_bold=True)
        
        # Horizontal line
        y_pos -= 12
        c.setStrokeColor(HexColor('#000000'))
        c.line(60, y_pos, page_width - 60, y_pos)
        
        # Contact information (right aligned, smaller)
        y_pos -= 18
        contact1 = self.reshape_arabic(t['contact1'], alanguage)
        if alanguage == 'ar':
            self.draw_right_text(c, contact1, y_pos, 9, x_margin=60)
        else:
            self.draw_left_text_wrapped(c, contact1, y_pos, 9, x_margin=60)
        
        y_pos -= 16
        contact2 = self.reshape_arabic(t['contact2'], alanguage)
        if alanguage == 'ar':
            self.draw_right_text(c, contact2, y_pos, 9, x_margin=60)
        else:
            self.draw_left_text_wrapped(c, contact2, y_pos, 9, x_margin=60)
        
        y_pos -= 16
        contact3 = self.reshape_arabic(t['contact3'], alanguage)
        if alanguage == 'ar':
            self.draw_right_text(c, contact3, y_pos, 9, x_margin=60)
        else:
            self.draw_left_text_wrapped(c, contact3, y_pos, 9, x_margin=60)
        
        # Save PDF
        c.save()
        print(f"✓ Certificate generated successfully: {output_path}")
        print(f"  Page size: FULL A4 ({page_width:.1f} x {page_height:.1f} points)")
        print(f"  Seuls les VALEURS des paramètres sont affichés en gras, les étiquettes sont normales (fr) | Only parameter values are in bold, labels are normal (ar)")


# Example usage
if __name__ == "__main__":
    # Try to find available fonts
    font_paths = [
        'Amiri-Regular.ttf', 
        'arial.ttf', 
        'NotoNaskhArabic-Regular.ttf', 
        'Scheherazade-Regular.ttf'
    ]
    
    bold_font_paths = [
        'Amiri-Bold.ttf',
        'arialbd.ttf',
        'NotoNaskhArabic-Bold.ttf',
        'Scheherazade-Bold.ttf'
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
    
    if font_file is None:
        print("\n" + "="*70)
        print("ERROR: No Arabic font found!")
        print("="*70)
        print("\nPlease download an Arabic font:")
        print("1. Amiri: https://fonts.google.com/specimen/Amiri")
        print("   - Download both Amiri-Regular.ttf and Amiri-Bold.ttf")
        print("2. Scheherazade: https://software.sil.org/scheherazade/")
        print("3. Noto Naskh Arabic: https://fonts.google.com/noto/specimen/Noto+Naskh+Arabic")
        print("\nPlace the TTF files in the same directory as this script.")
        print("="*70 + "\n")
        exit(1)
    
    # Initialize generator
    generator = ArabicCertificateGenerator(font_file, bold_font_file)
    
    # Certificate data - ONLY THE VALUES WILL BE BOLD (NOT THE LABELS)
    certificate_data = {
        'name': 'أحمد خليل',  # BOLD
        'surname': 'ورشي',  # BOLD
        'birth_date': '2004/01/28',  # BOLD
        'birth_place': 'ساقية سيدي يوسف',  # BOLD
        'national_id': '14440542',  # BOLD
        'registration_number': '22003013',  # BOLD
        'registration_code': 'GLSI2B',  # BOLD
        'year': '2023 - 2024',  # BOLD
        'certificate_type': 'الإجازة في علوم الإعلامية',  # BOLD
        'specialization': 'هندسة البرمجيات ونظم المعلومات',  # BOLD
        'grade': 'حسن',  # BOLD
        'issue_date': '2024/06/24'  # BOLD
    }
    
    # Arabic version
    generator.generate_certificate('certificate_full_a4_ar.pdf', alanguage='ar', **certificate_data)
    # French version
    certificate_data_fr = certificate_data.copy()
    certificate_data_fr.update({
        'name': 'Ahmed Khalil',
        'surname': 'Ouergui',
        'birth_place': 'Sakiet Sidi Youssef',
        'registration_code': 'GLSI2B',
        'certificate_type': 'Licence en Informatique',
        'specialization': "Génie Logiciel et Systèmes d'Information",
        'grade': 'Bien',
        'issue_date': '24/06/2024',
    })
    generator.generate_certificate('certificate_full_a4_fr.pdf', alanguage='fr', **certificate_data_fr)