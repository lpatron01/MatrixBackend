from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid

class DocumentRequest(models.Model):
    class DocumentType(models.TextChoices):
        TRANSCRIPT = 'TRANSCRIPT', _('Relevé de notes')
        CERTIFICATE_PRESENCE = 'CERTIFICATE_PRESENCE', _('Attestation de présence')
        CERTIFICATE_SUCCESS = 'CERTIFICATE_SUCCESS', _('Attestation de réussite')
        CERTIFICATE_INSCRIPTION = 'CERTIFICATE_INSCRIPTION', _('Attestation d\'inscription')
        DIPLOMA = 'DIPLOMA', _('Diplôme')
        OTHER = 'OTHER', _('Autre')

    class Status(models.TextChoices):
        NEW = 'NEW', _('Nouveau')
        IN_PROGRESS = 'IN_PROGRESS', _('En cours')
        READY = 'READY', _('Prêt')
        REJECTED = 'REJECTED', _('Rejeté')
        DELIVERED = 'DELIVERED', _('Livré')

    class Language(models.TextChoices):
        ARABIC = 'ar', _('Arabe')
        FRENCH = 'fr', _('Français')
        
    class ReceptionType(models.TextChoices):
        ONLINE = 'ONLINE', _('En ligne')
        PERSONAL = 'PERSONAL', _('En personne')
        BOTH = 'BOTH', _('Les deux')
        
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='document_requests'
    )
    document_type = models.CharField(
        max_length=50,
        choices=DocumentType.choices,
        default=DocumentType.OTHER
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW
    )
    language = models.CharField(
        max_length=2,
        choices=Language.choices,
        default=Language.ARABIC
    )
    reception_type = models.CharField(
        max_length=20,
        choices=ReceptionType.choices,
        default=ReceptionType.BOTH
    )
    academic_year = models.CharField(max_length=9, help_text="Ex: 2023-2024", default="2025-2026")
    additional_info = models.TextField(blank=True, null=True)
    pdf_file = models.FileField(upload_to='document_requests/pdfs/demandes/', null=True, blank=True, max_length=255)
    pdf_requested_file = models.FileField(upload_to='document_requests/pdfs/requested/', null=True, blank=True, max_length=255)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.document_type} - {self.student} ({self.status})"

class DocumentRequestHistory(models.Model):
    document_request = models.ForeignKey(
        DocumentRequest,
        on_delete=models.CASCADE,
        related_name='history'
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    old_status = models.CharField(max_length=20, null=True, blank=True)
    new_status = models.CharField(max_length=20, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History for {self.document_request.id} at {self.date}"
