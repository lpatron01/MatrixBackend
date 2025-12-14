from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid


class Club(models.Model):
    """Club model for student clubs"""
    
    class Status(models.TextChoices):
        PENDING = 'pending', _('En attente')
        ACTIVE = 'active', _('Actif')
        INACTIVE = 'inactive', _('Inactif')
        REJECTED = 'rejected', _('Rejeté')

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    logo = models.ImageField(upload_to='clubs/logos/', null=True, blank=True)
    
    president = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='managed_clubs',
        limit_choices_to={'role': 'club_manager'}
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    members_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Club"
        verbose_name_plural = "Clubs"

    def __str__(self):
        return self.name


class ClubEvent(models.Model):
    """Events organized by clubs"""
    
    class Status(models.TextChoices):
        DRAFT = 'draft', _('Brouillon')
        PENDING = 'pending', _('En attente')
        APPROVED = 'approved', _('Approuvé')
        REJECTED = 'rejected', _('Rejeté')
        COMPLETED = 'completed', _('Terminé')
        CANCELLED = 'cancelled', _('Annulé')

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='events')
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=200)
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    
    expected_attendees = models.PositiveIntegerField(default=0)
    actual_attendees = models.PositiveIntegerField(null=True, blank=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_events'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Club Event"
        verbose_name_plural = "Club Events"

    def __str__(self):
        return f"{self.title} - {self.club.name} ({self.date})"


class ClubReport(models.Model):
    """Semester reports for clubs"""
    
    class Semester(models.TextChoices):
        S1 = 's1', _('Semestre 1')
        S2 = 's2', _('Semestre 2')

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='reports')
    
    semester = models.CharField(max_length=2, choices=Semester.choices)
    academic_year = models.CharField(max_length=9, help_text="Ex: 2024-2025")
    
    title = models.CharField(max_length=200)
    content = models.TextField(help_text="Detailed report content")
    
    events_organized = models.PositiveIntegerField(default=0)
    total_attendees = models.PositiveIntegerField(default=0)
    budget_used = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    achievements = models.TextField(blank=True)
    challenges = models.TextField(blank=True)
    next_semester_plans = models.TextField(blank=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_reports'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['club', 'semester', 'academic_year']
        verbose_name = "Club Report"
        verbose_name_plural = "Club Reports"

    def __str__(self):
        return f"{self.club.name} - {self.semester} {self.academic_year}"


class ClubAnnouncement(models.Model):
    """Announcements from administrators to club managers"""
    
    class Priority(models.TextChoices):
        LOW = 'low', _('Basse')
        MEDIUM = 'medium', _('Moyenne')
        HIGH = 'high', _('Haute')
        URGENT = 'urgent', _('Urgente')

    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    
    # Target specific clubs or all clubs
    target_clubs = models.ManyToManyField(Club, blank=True, related_name='announcements')
    is_global = models.BooleanField(default=True, help_text="If true, visible to all clubs")
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_announcements'
    )
    
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Club Announcement"
        verbose_name_plural = "Club Announcements"

    def __str__(self):
        return self.title
