from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid

class Reclamation(models.Model):
    class Category(models.TextChoices):
        ADMINISTRATION = 'ADMINISTRATION', _('Administration')
        ENSEIGNEMENT = 'ENSEIGNEMENT', _('Enseignement')
        INFRASTRUCTURE = 'INFRASTRUCTURE', _('Infrastructure')
        HARCELEMENT = 'HARCELEMENT', _('Harcèlement')
        AUTRES = 'AUTRES', _('Autres')

    class Status(models.TextChoices):
        NOUVEAU = 'NOUVEAU', _('Nouveau')
        EN_COURS = 'EN_COURS', _('En cours')
        RESOLU = 'RESOLU', _('Résolu')
        REJETE = 'REJETE', _('Rejeté')

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reclamations'
    )
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        default=Category.AUTRES
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NOUVEAU
    )
    description = models.TextField()
    file = models.FileField(upload_to='reclamations/', null=True, blank=True)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category} - {self.status} ({self.id})"

class ReclamationHistory(models.Model):
    reclamation = models.ForeignKey(
        Reclamation,
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
        return f"History for {self.reclamation.id} at {self.date}"
