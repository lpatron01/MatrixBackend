from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class StudentGroup(models.Model):
    """Student groups/classes (e.g., 1A, 2B, 3INFO)"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    level = models.CharField(max_length=20, blank=True)  # e.g., L1, L2, L3, M1, M2
    specialty = models.CharField(max_length=100, blank=True)  # e.g., Informatique, Electrique
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Subject(models.Model):
    """Subjects/Courses"""
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    coefficient = models.DecimalField(max_digits=3, decimal_places=1, default=1.0)
    hours_cours = models.IntegerField(default=0)  # Total hours for cours
    hours_td = models.IntegerField(default=0)  # Total hours for TD
    hours_tp = models.IntegerField(default=0)  # Total hours for TP
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['code']


class Session(models.Model):
    """A single session/class in the schedule"""
    
    class SessionType(models.TextChoices):
        COURS = 'COURS', _('Cours Magistral')
        TD = 'TD', _('Travaux Dirigés')
        TP = 'TP', _('Travaux Pratiques')
        EXAMEN = 'EXAMEN', _('Examen')
        RATTRAPAGE = 'RATTRAPAGE', _('Rattrapage')

    class DayOfWeek(models.IntegerChoices):
        MONDAY = 1, _('Lundi')
        TUESDAY = 2, _('Mardi')
        WEDNESDAY = 3, _('Mercredi')
        THURSDAY = 4, _('Jeudi')
        FRIDAY = 5, _('Vendredi')
        SATURDAY = 6, _('Samedi')
        SUNDAY = 0, _('Dimanche')

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='sessions')
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='teaching_sessions',
        limit_choices_to={'role': 'teacher'}
    )
    group = models.ForeignKey(StudentGroup, on_delete=models.CASCADE, related_name='sessions')
    session_type = models.CharField(max_length=20, choices=SessionType.choices, default=SessionType.COURS)
    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50)
    
    # For specific date sessions (exams, exceptional sessions)
    specific_date = models.DateField(null=True, blank=True)
    is_recurring = models.BooleanField(default=True)
    
    # Semester/Period
    semester = models.CharField(max_length=20, default='S1')  # S1, S2
    academic_year = models.CharField(max_length=10, default='2024-2025')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject.name} - {self.get_session_type_display()} ({self.get_day_of_week_display()} {self.start_time}-{self.end_time})"

    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = [
            ['group', 'day_of_week', 'start_time', 'is_recurring', 'semester', 'academic_year'],
        ]


class Attendance(models.Model):
    """Attendance record for a student in a session"""
    
    class Status(models.TextChoices):
        PRESENT = 'PRESENT', _('Présent')
        ABSENT = 'ABSENT', _('Absent')
        LATE = 'LATE', _('En retard')
        EXCUSED = 'EXCUSED', _('Excusé')

    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='schedule_attendances')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='schedule_attendances',
        limit_choices_to={'role': 'student'}
    )
    date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ABSENT)
    
    # Justification for absence
    is_justified = models.BooleanField(default=False)
    justification = models.TextField(blank=True, null=True)
    justification_file = models.FileField(upload_to='justifications/', blank=True, null=True)
    
    # Who marked this attendance
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='schedule_marked_attendances'
    )
    marked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.email} - {self.session.subject.name} ({self.date}) - {self.get_status_display()}"

    class Meta:
        ordering = ['-date', 'session']
        unique_together = ['session', 'student', 'date']


class StudentGroupMembership(models.Model):
    """Links students to their groups"""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='group_memberships',
        limit_choices_to={'role': 'student'}
    )
    group = models.ForeignKey(StudentGroup, on_delete=models.CASCADE, related_name='members')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.student.email} -> {self.group.name}"

    class Meta:
        unique_together = ['student', 'group']
