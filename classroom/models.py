from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone


class Class(models.Model):
    """Academic class (e.g., 1A, 2B, etc.)"""
    name = models.CharField(max_length=50, unique=True, help_text="Class name (e.g., 1A, 2B)")
    description = models.CharField(max_length=200, blank=True)
    academic_year = models.CharField(max_length=9, help_text="Academic year (e.g., 2024-2025)", default="2024-2025")
    is_active = models.BooleanField(default=True)

    # Students in this class (many-to-many relationship)
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='classes',
        limit_choices_to={'role': 'student'},
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.academic_year})"


class Subject(models.Model):
    """Academic subject/course"""
    name = models.CharField(max_length=100, unique=True)
    name_arabic = models.CharField(max_length=100, blank=True)
    code = models.CharField(max_length=20, unique=True, help_text="Subject code (e.g., MATH101)")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Timetable(models.Model):
    """Weekly timetable entry"""

    class DayOfWeek(models.TextChoices):
        MONDAY = 'monday', _('Monday')
        TUESDAY = 'tuesday', _('Tuesday')
        WEDNESDAY = 'wednesday', _('Wednesday')
        THURSDAY = 'thursday', _('Thursday')
        FRIDAY = 'friday', _('Friday')

    class TimeSlot(models.TextChoices):
        S1 = 'S1', _('8:30 - 10:00')
        S2 = 'S2', _('10:05 - 11:35')
        S3 = 'S3', _('11:40 - 13:10')
        S4 = 'S4', _('14:00 - 15:30')
        S5 = 'S5', _('15:35 - 17:05')

    class_room = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='timetable_entries')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='timetable_entries')
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='timetable_entries',
        limit_choices_to={'role': 'teacher'}
    )
    day_of_week = models.CharField(max_length=10, choices=DayOfWeek.choices)
    time_slot = models.CharField(max_length=2, choices=TimeSlot.choices)
    classroom = models.CharField(max_length=50, help_text="Physical classroom location (e.g., Room 101)")
    academic_year = models.CharField(max_length=9, help_text="Academic year (e.g., 2024-2025)", default="2024-2025")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['class_room', 'day_of_week', 'time_slot', 'academic_year']
        ordering = ['day_of_week', 'time_slot']

    def __str__(self):
        return f"{self.class_room.name} - {self.day_of_week} {self.time_slot}: {self.subject.name}"

    def get_time_slot_display(self):
        """Get human-readable time slot"""
        times = {
            'S1': '8:30 - 10:00',
            'S2': '10:05 - 11:35',
            'S3': '11:40 - 13:10',
            'S4': '14:00 - 15:30',
            'S5': '15:35 - 17:05'
        }
        return times.get(self.time_slot, self.time_slot)


class Attendance(models.Model):
    """Student attendance record for a specific session"""

    class Status(models.TextChoices):
        PRESENT = 'present', _('Present')
        ABSENT = 'absent', _('Absent')
        LATE = 'late', _('Late')
        EXCUSED = 'excused', _('Excused')

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        limit_choices_to={'role': 'student'}
    )
    timetable_entry = models.ForeignKey(
        Timetable,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
    remarks = models.TextField(blank=True, help_text="Additional notes about attendance")
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='marked_attendances',
        limit_choices_to={'role': 'teacher'}
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'timetable_entry', 'date']
        ordering = ['-date', 'timetable_entry__time_slot']

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.timetable_entry} ({self.date}) - {self.status}"

    def clean(self):
        """Validate that student is in the class for this timetable entry"""
        if not self.timetable_entry.class_room.students.filter(id=self.student.id).exists():
            raise ValidationError(
                f"Student {self.student.get_full_name()} is not enrolled in class {self.timetable_entry.class_room.name}"
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
