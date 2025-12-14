from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging
from .models import Reclamation
from .serializers import (
    ReclamationSerializer,
    ReclamationCreateSerializer,
    ReclamationAdminUpdateSerializer
)
from users.models import User

logger = logging.getLogger(__name__)

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_staff or request.user.role == User.Role.ADMINISTRATOR)

class ReclamationListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'is_anonymous']
    ordering_fields = ['created_at', 'status']

    def get_queryset(self):
        user = self.request.user
        # Admins see all
        if user.is_staff or user.role == User.Role.ADMINISTRATOR:
            return Reclamation.objects.all()
        # Teachers see only ENSEIGNEMENT category
        elif user.role == User.Role.TEACHER:
            return Reclamation.objects.filter(category=Reclamation.Category.ENSEIGNEMENT)
        # Students see their own
        return Reclamation.objects.filter(student=user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReclamationCreateSerializer
        return ReclamationSerializer

    def perform_create(self, serializer):
        # Always associate the student so they can track their reclamation
        # Anonymity is handled in the serializer representation
        serializer.save(student=self.request.user)

class ReclamationDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'public_id'
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == User.Role.ADMINISTRATOR:
            return Reclamation.objects.all()
        elif user.role == User.Role.TEACHER:
            return Reclamation.objects.filter(category=Reclamation.Category.ENSEIGNEMENT)
        return Reclamation.objects.filter(student=user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            # Only admins should be using this serializer effectively to change status
            return ReclamationAdminUpdateSerializer
        return ReclamationSerializer

    def perform_update(self, serializer):
        # Check permission for update
        user = self.request.user
        if not (user.is_staff or user.role == User.Role.ADMINISTRATOR or user.role == User.Role.TEACHER):
             raise permissions.PermissionDenied("You do not have permission to update this reclamation.")

        # Store the old status for comparison
        old_status = self.get_object().status

        # Save the update
        serializer.save()

        # Get the updated instance
        instance = self.get_object()
        new_status = instance.status

        # Send email notification if status changed and student is not anonymous
        if old_status != new_status and not instance.is_anonymous:
            self._send_status_update_email(instance)

    def _send_status_update_email(self, reclamation):
        """Send email notification to student about status update"""
        student = reclamation.student

        # Prepare email context
        context = {
            'student_name': student.first_name or student.email,
            'category': reclamation.get_category_display(),
            'status': reclamation.status,
            'status_display': reclamation.get_status_display(),
            'comment': reclamation.comment or '',
            'reclamation_url': f"{settings.FRONTEND_URL}/student/reclamations/{reclamation.public_id}" if hasattr(settings, 'FRONTEND_URL') else f"/student/reclamations/{reclamation.public_id}"
        }

        # Prepare email content
        subject = f"Statut de votre réclamation mis à jour - {reclamation.get_status_display()}"
        html_message = render_to_string('emails/reclamations/status_updated.html', context)
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
            logger.info(f"Email sent to student {student.email} about status update for reclamation {reclamation.public_id}")
        except Exception as e:
            logger.error(f"Failed to send email to student {student.email}: {str(e)}")

    def perform_destroy(self, instance):
        user = self.request.user
        if user.is_staff or user.role == User.Role.ADMINISTRATOR:
            instance.delete()
        # Student can only delete their own reclamation
        elif instance.student == user:
            instance.delete()
        else:
            raise permissions.PermissionDenied("You do not have permission to delete this reclamation.")
