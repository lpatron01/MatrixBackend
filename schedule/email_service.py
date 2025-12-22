"""
Email notification services for the schedule module.
Sends emails for absences and eliminations.
"""
import logging
from datetime import datetime
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

logger = logging.getLogger(__name__)

ELIMINATION_THRESHOLD = 4  # Number of absences before elimination


def send_absence_notification(student, session, attendance, absence_count):
    """
    Send email notification when a student is marked absent.
    
    Args:
        student: User object (student)
        session: Session object
        attendance: Attendance object
        absence_count: Total absences in this subject
    """
    try:
        context = {
            'student_name': f"{student.first_name} {student.last_name}",
            'subject_name': session.subject.name,
            'date': attendance.date.strftime('%d/%m/%Y'),
            'start_time': session.start_time.strftime('%H:%M'),
            'end_time': session.end_time.strftime('%H:%M'),
            'teacher_name': f"{session.teacher.first_name} {session.teacher.last_name}" if session.teacher else "Non assigné",
            'absence_count': absence_count,
            'year': datetime.now().year
        }
        
        subject = f"⚠️ Notification d'absence - {session.subject.name}"
        html_message = render_to_string('emails/absences/absence_notification.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student.email],
            html_message=html_message,
            fail_silently=True,
        )
        
        logger.info(f"Absence notification sent to {student.email} for {session.subject.name}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send absence notification to {student.email}: {str(e)}")
        return False


def send_elimination_notification(student, session, attendance, absence_count):
    """
    Send email notification when a student is eliminated (4+ absences).
    
    Args:
        student: User object (student)
        session: Session object
        attendance: Attendance object
        absence_count: Total absences in this subject
    """
    try:
        context = {
            'student_name': f"{student.first_name} {student.last_name}",
            'subject_name': session.subject.name,
            'date': attendance.date.strftime('%d/%m/%Y'),
            'teacher_name': f"{session.teacher.first_name} {session.teacher.last_name}" if session.teacher else "Non assigné",
            'absence_count': absence_count,
            'year': datetime.now().year
        }
        
        subject = f"🚨 ALERTE ÉLIMINATION - {session.subject.name}"
        html_message = render_to_string('emails/absences/elimination_notification.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student.email],
            html_message=html_message,
            fail_silently=True,
        )
        
        logger.info(f"Elimination notification sent to {student.email} for {session.subject.name} (absences: {absence_count})")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send elimination notification to {student.email}: {str(e)}")
        return False


def notify_student_absence(student, session, attendance):
    """
    Main function to handle absence notifications.
    Automatically determines if it's a simple absence or elimination.
    
    Args:
        student: User object (student)
        session: Session object
        attendance: Attendance object
    
    Returns:
        dict with notification status
    """
    from .models import Attendance
    
    # Count absences for this student in this subject
    absence_count = Attendance.objects.filter(
        student=student,
        session__subject=session.subject,
        status=Attendance.Status.ABSENT,
        session__semester=session.semester,
        session__academic_year=session.academic_year
    ).count()
    
    result = {
        'absence_count': absence_count,
        'is_eliminated': absence_count >= ELIMINATION_THRESHOLD,
        'notification_sent': False,
        'elimination_notification_sent': False
    }
    
    # Always send absence notification
    result['notification_sent'] = send_absence_notification(
        student, session, attendance, absence_count
    )
    
    # If eliminated, send elimination notification
    if absence_count >= ELIMINATION_THRESHOLD:
        result['elimination_notification_sent'] = send_elimination_notification(
            student, session, attendance, absence_count
        )
    
    return result
