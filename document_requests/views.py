from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import DocumentRequest, PresenceRequestApproval
from .serializers import (
    DocumentRequestSerializer,
    DocumentRequestCreateSerializer,
    DocumentRequestAdminUpdateSerializer,
    DocumentRequestedFileSerializer,
    PresenceRequestCreateSerializer,
    PresenceRequestApprovalSerializer,
    PresenceRequestApprovalUpdateSerializer
)
from users.models import User, EducationHistory
from .utlils.demande import generate_document_request_pdf
from .utlils.inscri import KairouanTarsimCertificateGenerator as InscriptionCertificateGenerator
from .utlils.presence import KairouanTarsimCertificateGenerator as PresenceCertificateGenerator
from .utlils.sucess import ArabicCertificateGenerator as SuccessCertificateGenerator
from django.http import FileResponse, Http404
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import os,logging
from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger(__name__)

class DocumentRequestListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['document_type', 'status']
    ordering_fields = ['created_at', 'status']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == User.Role.ADMINISTRATOR:
            return DocumentRequest.objects.all()
        return DocumentRequest.objects.filter(student=user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DocumentRequestCreateSerializer
        return DocumentRequestSerializer

    def perform_create(self, serializer):
        document_request = serializer.save(student=self.request.user)
        # Generate PDF and save its path
        pdf_path = generate_document_request_pdf(document_request)
        document_request.pdf_file = pdf_path
        document_request.save()

class DocumentRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'public_id'
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == User.Role.ADMINISTRATOR:
            return DocumentRequest.objects.all()
        return DocumentRequest.objects.filter(student=user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DocumentRequestAdminUpdateSerializer
        return DocumentRequestSerializer

    def perform_update(self, serializer):
        user = self.request.user
        if not (user.is_staff or user.role == User.Role.ADMINISTRATOR):
             raise permissions.PermissionDenied("You do not have permission to update this request.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if user.is_staff or user.role == User.Role.ADMINISTRATOR:
            instance.delete()
        elif instance.student == user:
            instance.delete()
        else:
            raise permissions.PermissionDenied("You do not have permission to delete this request.")


class TerminateDocumentRequestView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'public_id'
    serializer_class = DocumentRequestAdminUpdateSerializer

    def get_queryset(self):
        return DocumentRequest.objects.all()

    def perform_update(self, serializer):
        user = self.request.user
        if not (user.is_staff or user.role == User.Role.ADMINISTRATOR):
            raise permissions.PermissionDenied("You do not have permission to terminate this request.")
        serializer.instance.status = DocumentRequest.Status.READY
        serializer.save(changed_by=user, comment="Demande terminée.")

        # Send email notification to student
        self._send_status_update_email(serializer.instance, user)

class RejectDocumentRequestView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'public_id'
    serializer_class = DocumentRequestAdminUpdateSerializer

    def get_queryset(self):
        return DocumentRequest.objects.all()

    def perform_update(self, serializer):
        user = self.request.user
        if not (user.is_staff or user.role == User.Role.ADMINISTRATOR):
            raise permissions.PermissionDenied("You do not have permission to reject this request.")
        serializer.instance.status = DocumentRequest.Status.REJECTED
        serializer.save(changed_by=user, comment="Demande rejetée.")

        # Send email notification to student
        self._send_status_update_email(serializer.instance, user)

class ProcessDocumentRequestView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'public_id'
    serializer_class = DocumentRequestAdminUpdateSerializer

    def get_queryset(self):
        return DocumentRequest.objects.all()

    def perform_update(self, serializer):
        user = self.request.user
        if not (user.is_staff or user.role == User.Role.ADMINISTRATOR):
            raise permissions.PermissionDenied("You do not have permission to process this request.")
        serializer.instance.status = DocumentRequest.Status.IN_PROGRESS
        serializer.save(changed_by=user, comment="Demande en cours de traitement.")

        # Send email notification to student
        self._send_status_update_email(serializer.instance, user)


class DocumentRequestFileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'public_id'

    def get_queryset(self):
        return DocumentRequest.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user

        if not (user.is_staff or user.role == User.Role.ADMINISTRATOR):
            raise permissions.PermissionDenied("You do not have permission to access this file.")

        if not instance.pdf_file:
            raise Http404("PDF file not found for this document request.")
        
        try:
            return FileResponse(instance.pdf_file.open(), content_type='application/pdf')
        except FileNotFoundError:
            raise Http404("PDF file not found on the server.")

class DocumentRequestUploadFileView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'public_id'
    serializer_class = DocumentRequestedFileSerializer

    def get_queryset(self):
        return DocumentRequest.objects.all()

    def perform_update(self, serializer):
        user = self.request.user
        if not (user.is_staff or user.role == User.Role.ADMINISTRATOR):
            raise permissions.PermissionDenied("You do not have permission to upload this file.")
        serializer.save()

    def _send_status_update_email(self, document_request, changed_by=None):
        """Send email notification to student about status update"""
        student = document_request.student

        # Prepare email context
        context = {
            'student_name': student.first_name or student.email,
            'document_type': document_request.get_document_type_display(),
            'status': document_request.status,
            'status_display': document_request.get_status_display(),
            'academic_year': document_request.academic_year,
            'language_display': document_request.get_language_display(),
            'comment': getattr(document_request, 'comment', '') or '',
            'request_url': f"{settings.FRONTEND_URL}/student/documents/{document_request.public_id}" if hasattr(settings, 'FRONTEND_URL') else f"/student/documents/{document_request.public_id}",
            'download_url': f"{settings.FRONTEND_URL}/student/documents/{document_request.public_id}/download" if hasattr(settings, 'FRONTEND_URL') else f"/student/documents/{document_request.public_id}/download"
        }

        # Prepare email content
        subject = f"Statut de votre demande de document mis à jour - {document_request.get_status_display()}"
        html_message = render_to_string('emails/documents/status_updated.html', context)
        plain_message = strip_tags(html_message)

        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"Email sent to student {student.email} about status update for document request {document_request.public_id}")
        except Exception as e:
            logger.error(f"Failed to send email to student {student.email}: {str(e)}")

class GenerateInscriptionCertificateView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'public_id'

    def get_queryset(self):
        return DocumentRequest.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user

        if not (user.is_staff or user.role == User.Role.ADMINISTRATOR or instance.student == user):
            raise permissions.PermissionDenied("You do not have permission to access this certificate.")
        
        if instance.document_type != DocumentRequest.DocumentType.CERTIFICATE_INSCRIPTION:
            raise Http404("This document request is not for an inscription certificate.")

        alanguage = request.query_params.get('lang', instance.language) # Default to request language, then instance language

        # Retrieve student information from the database
        student = instance.student
        
        # Fetch the education history for the academic year of the document request
        education_history = None
        try:
            education_history = student.education_histories.get(academic_year=instance.academic_year)
        except student.education_histories.model.DoesNotExist:
            # Fallback to the most recent education history if the specific year isn't found
            education_history = student.education_histories.order_by('-academic_year').first()
            if education_history:
                logger.warning(f"Education history for academic year {instance.academic_year} not found. Using most recent ({education_history.academic_year}).")
            else:
                logger.warning("No education history found for student.")

        # Prepare certificate data
        certificate_data = {
            'name': student.first_name_arabic if alanguage == 'ar' else student.first_name,
            'surname': student.last_name_arabic if alanguage == 'ar' else student.last_name,
            'birth_date': student.date_of_birth.strftime('%Y/%m/%d') if student.date_of_birth else '',
            'birth_place': student.place_of_birth_arabic if alanguage == 'ar' else student.place_of_birth,
            'national_id': str(student.cin) if student.cin else '',
            'year_class': EducationHistory.Grade.get_grade_display_by_language(education_history.grade, alanguage) if education_history else '',
            'registration_code': education_history.class_name if education_history else '',
            'certificate_type': User.DiplomaChoices.get_diploma_display_by_language(student.diploma, alanguage), # Use diploma from User model based on language
            'specialization': 'جذع مشترك' if alanguage == 'ar' else education_history.specialty   ,
            'registration_number': str(education_history.registration_id) if education_history else '',
            'year': instance.academic_year, # Use academic year from document request
            'issue_date': instance.updated_at.strftime('%Y/%m/%d') if instance.updated_at else '',
        }

        if alanguage == 'fr':
            # Ensure birth_date and issue_date are handled as single strings, not tuples
            certificate_data['birth_date'] = student.date_of_birth.strftime('%d/%m/%Y') if student.date_of_birth else ''
            certificate_data['issue_date'] = instance.updated_at.strftime('%d/%m/%Y') if instance.updated_at else ''

        # Get font paths (assuming they are in the same directory as inscri.py or accessible)
        # For a production environment, you'd manage font paths more robustly (e.g., settings.py)
        font_file = 'Amiri-Regular.ttf'
        bold_font_file = 'Amiri-Bold.ttf'

        # Check if font files exist relative to the inscri.py file
        # Import logging for consistent logging practices
        # The path construction for fonts is already handled within KairouanTarsimCertificateGenerator's __init__
        # We just need to pass the base font filenames.
        
        generator = KairouanTarsimCertificateGenerator(font_path=font_file, bold_font_path=bold_font_file, alanguage=alanguage)
        
        # Define a temporary path for the PDF
        temp_pdf_name = f"inscription_certificate_{instance.public_id}_{alanguage}.pdf"
        temp_pdf_path = os.path.join(settings.MEDIA_ROOT, 'temp_pdfs', temp_pdf_name)
        os.makedirs(os.path.dirname(temp_pdf_path), exist_ok=True) # Ensure directory exists

        # Attempt to generate the certificate
        pdf_generated = generator.generate_certificate(temp_pdf_path, alanguage=alanguage, **certificate_data)

        if not pdf_generated: # If generate_certificate returned None due to font issues
            logger.error(f"Failed to generate PDF for request {instance.public_id} due to font errors. Check inscri.py logs for details.")
            return Response({"detail": "Failed to generate certificate due to server-side font configuration issues."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            return FileResponse(open(temp_pdf_path, 'rb'), content_type='application/pdf')
        except FileNotFoundError:
            logger.error(f"Generated PDF file not found on the server at {temp_pdf_path} after generation attempt.")
            raise Http404("Generated PDF file not found on the server.")
        # Note: Temporary file cleanup is handled by periodic cleanup task or manual cleanup
        # to avoid permission errors while the file is being served


class GeneratePresenceCertificateView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'public_id'

    def get_queryset(self):
        return DocumentRequest.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user

        if not (user.is_staff or user.role == User.Role.ADMINISTRATOR or instance.student == user):
            raise permissions.PermissionDenied("You do not have permission to access this certificate.")

        if instance.document_type != DocumentRequest.DocumentType.CERTIFICATE_PRESENCE:
            raise Http404("This document request is not for a presence certificate.")

        alanguage = request.query_params.get('lang', instance.language) # Default to request language, then instance language

        # Retrieve student information from the database
        student = instance.student

        # Fetch the education history for the academic year of the document request
        education_history = None
        try:
            education_history = student.education_histories.get(academic_year=instance.academic_year)
        except student.education_histories.model.DoesNotExist:
            # Fallback to the most recent education history if the specific year isn't found
            education_history = student.education_histories.order_by('-academic_year').first()
            if education_history:
                logger.warning(f"Education history for academic year {instance.academic_year} not found. Using most recent ({education_history.academic_year}).")
            else:
                logger.warning("No education history found for student.")

        # Prepare certificate data
        certificate_data = {
            'name': student.first_name_arabic if alanguage == 'ar' else student.first_name,
            'surname': student.last_name_arabic if alanguage == 'ar' else student.last_name,
            'birth_date': student.date_of_birth.strftime('%Y/%m/%d') if student.date_of_birth else '',
            'birth_place': student.place_of_birth_arabic if alanguage == 'ar' else student.place_of_birth,
            'national_id': str(student.cin) if student.cin else '',
            'year_class': EducationHistory.Grade.get_grade_display_by_language(education_history.grade, alanguage) if education_history else '',
            'registration_code': education_history.class_name if education_history else '',
            'certificate_type': User.DiplomaChoices.get_diploma_display_by_language(student.diploma, alanguage), # Use diploma from User model based on language
            'specialization': 'جذع مشترك' if alanguage == 'ar' else education_history.specialty,
            'registration_number': str(education_history.registration_id) if education_history else '',
            'year': instance.academic_year, # Use academic year from document request
            'issue_date': instance.updated_at.strftime('%Y/%m/%d') if instance.updated_at else '',
        }

        if alanguage == 'fr':
            # Ensure birth_date and issue_date are handled as single strings, not tuples
            certificate_data['birth_date'] = student.date_of_birth.strftime('%d/%m/%Y') if student.date_of_birth else ''
            certificate_data['issue_date'] = instance.updated_at.strftime('%d/%m/%Y') if instance.updated_at else ''

        # Get font paths (assuming they are in the same directory as presence.py or accessible)
        # For a production environment, you'd manage font paths more robustly (e.g., settings.py)
        font_file = 'Amiri-Regular.ttf'
        bold_font_file = 'Amiri-Bold.ttf'

        # Check if font files exist relative to the presence.py file
        # Import logging for consistent logging practices
        # The path construction for fonts is already handled within KairouanTarsimCertificateGenerator's __init__
        # We just need to pass the base font filenames.

        generator = PresenceCertificateGenerator(font_path=font_file, bold_font_path=bold_font_file, alanguage=alanguage)

        # Define a temporary path for the PDF
        temp_pdf_name = f"presence_certificate_{instance.public_id}_{alanguage}.pdf"
        temp_pdf_path = os.path.join(settings.MEDIA_ROOT, 'temp_pdfs', temp_pdf_name)
        os.makedirs(os.path.dirname(temp_pdf_path), exist_ok=True) # Ensure directory exists

        # Attempt to generate the certificate
        pdf_generated = generator.generate_certificate(temp_pdf_path, alanguage=alanguage, **certificate_data)

        if not pdf_generated: # If generate_certificate returned None due to font issues
            logger.error(f"Failed to generate PDF for request {instance.public_id} due to font errors. Check presence.py logs for details.")
            return Response({"detail": "Failed to generate certificate due to server-side font configuration issues."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            return FileResponse(open(temp_pdf_path, 'rb'), content_type='application/pdf')
        except FileNotFoundError:
            logger.error(f"Generated PDF file not found on the server at {temp_pdf_path} after generation attempt.")
            raise Http404("Generated PDF file not found on the server.")
        # Note: Temporary file cleanup is handled by periodic cleanup task or manual cleanup
        # to avoid permission errors while the file is being served


class PresenceRequestCreateView(generics.CreateAPIView):
    """View for students to create presence certificate requests with teacher selection"""
    serializer_class = PresenceRequestCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        document_request = serializer.save(student=self.request.user)

        # Send email notifications to teachers
        self._send_teacher_notifications(document_request)

        # Generate PDF and save its path
        pdf_path = generate_document_request_pdf(document_request)
        document_request.pdf_file = pdf_path
        document_request.save()

    def _send_teacher_notifications(self, document_request):
        """Send email notifications to teachers for approval"""
        approvals = document_request.presence_approvals.all()

        for approval in approvals:
            teacher = approval.teacher
            student = document_request.student

            # Prepare email context
            context = {
                'teacher_name': teacher.first_name or teacher.email,
                'student_name': f"{student.first_name} {student.last_name}",
                'request_id': str(document_request.public_id),
                'language': document_request.get_language_display(),
                'reception_type': document_request.get_reception_type_display(),
                'academic_year': document_request.academic_year,
                'approval_url': f"{settings.FRONTEND_URL}/teacher/approvals/{approval.id}" if hasattr(settings, 'FRONTEND_URL') else f"/teacher/approvals/{approval.id}"
            }

            # Render email templates
            subject = "Nouvelle demande d'attestation de présence à approuver"
            html_message = render_to_string('emails/presence_request_notification.html', context)
            plain_message = strip_tags(html_message)

            try:
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[teacher.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                logger.info(f"Email sent to teacher {teacher.email} for presence request {document_request.public_id}")
            except Exception as e:
                logger.error(f"Failed to send email to teacher {teacher.email}: {str(e)}")


class PresenceRequestApprovalListView(generics.ListAPIView):
    """View for teachers to see their pending presence request approvals"""
    serializer_class = PresenceRequestApprovalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role != User.Role.TEACHER:
            return PresenceRequestApproval.objects.none()

        return PresenceRequestApproval.objects.filter(
            teacher=user,
            status=PresenceRequestApproval.ApprovalStatus.PENDING
        ).select_related('document_request', 'document_request__student')


class PresenceRequestApprovalDetailView(generics.RetrieveUpdateAPIView):
    """View for teachers to approve or reject presence requests"""
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        if user.role != User.Role.TEACHER:
            return PresenceRequestApproval.objects.none()

        return PresenceRequestApproval.objects.filter(
            teacher=user
        ).select_related('document_request', 'document_request__student')

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PresenceRequestApprovalUpdateSerializer
        return PresenceRequestApprovalSerializer

    def perform_update(self, serializer):
        approval = serializer.save()

        # Send notification email to student about the approval/rejection
        self._send_student_notification(approval)

    def _send_student_notification(self, approval):
        """Send email notification to student about approval/rejection status"""
        document_request = approval.document_request
        student = document_request.student
        teacher = approval.teacher

        context = {
            'student_name': student.first_name or student.email,
            'teacher_name': f"{teacher.first_name} {teacher.last_name}",
            'request_id': str(document_request.public_id),
            'status': approval.get_status_display(),
            'comment': approval.comment or '',
            'request_url': f"{settings.FRONTEND_URL}/student/requests/{document_request.public_id}" if hasattr(settings, 'FRONTEND_URL') else f"/student/requests/{document_request.public_id}"
        }

        if approval.status == PresenceRequestApproval.ApprovalStatus.APPROVED:
            subject = "Votre demande d'attestation de présence a été approuvée"
            template = 'emails/presence_request_approved.html'
        else:
            subject = "Votre demande d'attestation de présence a été rejetée"
            template = 'emails/presence_request_rejected.html'

        try:
            html_message = render_to_string(template, context)
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"Email sent to student {student.email} about approval status change for request {document_request.public_id}")
        except Exception as e:
            logger.error(f"Failed to send email to student {student.email}: {str(e)}")


class GenerateSuccessCertificateView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'public_id'

    def get_queryset(self):
        return DocumentRequest.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user

        if not (user.is_staff or user.role == User.Role.ADMINISTRATOR or instance.student == user):
            raise permissions.PermissionDenied("You do not have permission to access this certificate.")

        if instance.document_type != DocumentRequest.DocumentType.CERTIFICATE_SUCCESS:
            raise Http404("This document request is not for a success certificate.")

        alanguage = request.query_params.get('lang', instance.language) # Default to request language, then instance language

        # Retrieve student information from the database
        student = instance.student

        # Fetch the education history for the academic year of the document request
        education_history = None
        try:
            education_history = student.education_histories.get(academic_year=instance.academic_year)
        except student.education_histories.model.DoesNotExist:
            # Fallback to the most recent education history if the specific year isn't found
            education_history = student.education_histories.order_by('-academic_year').first()
            if education_history:
                logger.warning(f"Education history for academic year {instance.academic_year} not found. Using most recent ({education_history.academic_year}).")
            else:
                logger.warning("No education history found for student.")

        # Prepare certificate data
        certificate_data = {
            'name': student.first_name_arabic if alanguage == 'ar' else student.first_name,
            'surname': student.last_name_arabic if alanguage == 'ar' else student.last_name,
            'birth_date': student.date_of_birth.strftime('%Y/%m/%d') if student.date_of_birth else '',
            'birth_place': student.place_of_birth_arabic if alanguage == 'ar' else student.place_of_birth,
            'national_id': str(student.cin) if student.cin else '',
            'registration_number': str(education_history.registration_id) if education_history else '',
            'registration_code': education_history.class_name if education_history else '',
            'year': instance.academic_year, # Use academic year from document request
            'certificate_type': User.DiplomaChoices.get_diploma_display_by_language(student.diploma, alanguage), # Use diploma from User model based on language
            'specialization': 'جذع مشترك' if alanguage == 'ar' else education_history.specialty,
            'grade': 'حسن' if alanguage == 'ar' else 'Bien',  # Default grade, could be made dynamic
            'issue_date': instance.updated_at.strftime('%Y/%m/%d') if instance.updated_at else '',
        }

        if alanguage == 'fr':
            # Ensure birth_date and issue_date are handled as single strings, not tuples
            certificate_data['birth_date'] = student.date_of_birth.strftime('%d/%m/%Y') if student.date_of_birth else ''
            certificate_data['issue_date'] = instance.updated_at.strftime('%d/%m/%Y') if instance.updated_at else ''

        # Get font paths (assuming they are in the same directory as sucess.py or accessible)
        # For a production environment, you'd manage font paths more robustly (e.g., settings.py)
        font_file = 'Amiri-Regular.ttf'
        bold_font_file = 'Amiri-Bold.ttf'

        # Check if font files exist relative to the sucess.py file
        # Import logging for consistent logging practices
        # The path construction for fonts is already handled within ArabicCertificateGenerator's __init__
        # We just need to pass the base font filenames.

        generator = SuccessCertificateGenerator(font_path=font_file, bold_font_path=bold_font_file, alanguage=alanguage)

        # Define a temporary path for the PDF
        temp_pdf_name = f"success_certificate_{instance.public_id}_{alanguage}.pdf"
        temp_pdf_path = os.path.join(settings.MEDIA_ROOT, 'temp_pdfs', temp_pdf_name)
        os.makedirs(os.path.dirname(temp_pdf_path), exist_ok=True) # Ensure directory exists

        # Attempt to generate the certificate
        pdf_generated = generator.generate_certificate(temp_pdf_path, alanguage=alanguage, **certificate_data)

        if not pdf_generated: # If generate_certificate returned None due to font issues
            logger.error(f"Failed to generate PDF for request {instance.public_id} due to font errors. Check sucess.py logs for details.")
            return Response({"detail": "Failed to generate certificate due to server-side font configuration issues."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            return FileResponse(open(temp_pdf_path, 'rb'), content_type='application/pdf')
        except FileNotFoundError:
            logger.error(f"Generated PDF file not found on the server at {temp_pdf_path} after generation attempt.")
            raise Http404("Generated PDF file not found on the server.")
        # Note: Temporary file cleanup is handled by periodic cleanup task or manual cleanup
        # to avoid permission errors while the file is being served