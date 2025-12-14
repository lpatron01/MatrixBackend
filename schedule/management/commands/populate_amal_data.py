from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from schedule.models import StudentGroup, Subject, Session, StudentGroupMembership, Attendance
from datetime import date, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates attendance data for student amal@gmail.com'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test data for amal@gmail.com...')

        # 1. Get or create the student
        student, created = User.objects.get_or_create(
            email='amal@gmail.com',
            defaults={
                'first_name': 'Amal',
                'last_name': 'Ben Ahmed',
                'role': User.Role.STUDENT,
                'is_active': True
            }
        )
        if created:
            student.set_password('password123')
            student.save()
            self.stdout.write(f'Created student: {student.email}')
        else:
            self.stdout.write(f'Found existing student: {student.email}')

        # 2. Get or create a teacher
        teacher, _ = User.objects.get_or_create(
            email='prof@issat.tn',
            defaults={
                'first_name': 'Mohamed',
                'last_name': 'Enseignant',
                'role': User.Role.TEACHER,
                'is_active': True
            }
        )
        if _:
            teacher.set_password('password123')
            teacher.save()

        # 3. Create group and assign student
        group, _ = StudentGroup.objects.get_or_create(
            name='2INFO-C',
            defaults={
                'description': '2ème année Informatique Groupe C',
                'level': 'L2',
                'specialty': 'Informatique'
            }
        )
        StudentGroupMembership.objects.get_or_create(student=student, group=group)
        self.stdout.write(f'Student assigned to group: {group.name}')

        # 4. Create subjects
        subjects_data = [
            {'name': 'Algorithmes Avancés', 'code': 'ALG3', 'coef': 3.0, 'h_c': 21, 'h_td': 10, 'h_tp': 20},
            {'name': 'Intelligence Artificielle', 'code': 'IA2', 'coef': 3.0, 'h_c': 21, 'h_td': 10, 'h_tp': 20},
            {'name': 'Réseaux Informatiques', 'code': 'NET2', 'coef': 2.0, 'h_c': 21, 'h_td': 10, 'h_tp': 10},
            {'name': 'Génie Logiciel', 'code': 'GL2', 'coef': 2.5, 'h_c': 21, 'h_td': 10, 'h_tp': 20},
            {'name': 'Français Technique', 'code': 'FR2', 'coef': 1.0, 'h_c': 0, 'h_td': 21, 'h_tp': 0},
        ]
        
        subjects = {}
        for sub in subjects_data:
            s, _ = Subject.objects.get_or_create(
                code=sub['code'],
                defaults={
                    'name': sub['name'],
                    'coefficient': sub['coef'],
                    'hours_cours': sub['h_c'],
                    'hours_td': sub['h_td'],
                    'hours_tp': sub['h_tp']
                }
            )
            subjects[sub['code']] = s
        self.stdout.write(f'Subjects created: {len(subjects)}')

        # 5. Create sessions for the week (today is Sunday = 0)
        today = date.today()
        today_day = today.weekday() + 1  # Python weekday: 0=Mon -> convert to 1=Mon for Django
        if today_day == 7:
            today_day = 0  # Sunday

        # Sessions for today (if Sunday, create for demonstration)
        # Let's create sessions for multiple days
        sessions_data = [
            # Today (Sunday = 0 or adjust for current day)
            (today_day or 1, '08:30:00', '10:00:00', 'ALG3', Session.SessionType.COURS, 'Amphi C'),
            (today_day or 1, '10:15:00', '11:45:00', 'IA2', Session.SessionType.TP, 'Lab 3'),
            (today_day or 1, '14:00:00', '15:30:00', 'NET2', Session.SessionType.TD, 'Salle 08'),
            # Other days
            (1, '08:30:00', '10:00:00', 'GL2', Session.SessionType.COURS, 'Salle 05'),  # Monday
            (2, '10:15:00', '11:45:00', 'FR2', Session.SessionType.TD, 'Salle 10'),    # Tuesday
            (3, '14:00:00', '15:30:00', 'ALG3', Session.SessionType.TP, 'Lab 1'),      # Wednesday
            (4, '08:30:00', '10:00:00', 'IA2', Session.SessionType.COURS, 'Amphi B'),  # Thursday
            (5, '10:15:00', '11:45:00', 'NET2', Session.SessionType.TP, 'Lab Réseau'), # Friday
        ]

        sessions = {}
        for day, start, end, sub_code, type_, room in sessions_data:
            try:
                session, _ = Session.objects.get_or_create(
                    group=group,
                    day_of_week=day,
                    start_time=start,
                    subject=subjects[sub_code],
                    semester='S1',
                    academic_year='2024-2025',
                    defaults={
                        'end_time': end,
                        'session_type': type_,
                        'room': room,
                        'teacher': teacher,
                        'is_recurring': True
                    }
                )
                sessions[f'{sub_code}_{day}_{start}'] = session
            except Exception as e:
                # Session already exists with different parameters, try to get it
                session = Session.objects.filter(
                    group=group,
                    day_of_week=day,
                    start_time=start,
                    semester='S1',
                    academic_year='2024-2025'
                ).first()
                if session:
                    sessions[f'{sub_code}_{day}_{start}'] = session
        self.stdout.write(f'Sessions created/found: {len(sessions)}')

        # 6. Create attendance records with various scenarios

        # Past dates for absences
        past_dates = [
            today - timedelta(days=7),
            today - timedelta(days=14),
            today - timedelta(days=21),
            today - timedelta(days=28),
            today - timedelta(days=35),
            today - timedelta(days=42),
            today - timedelta(days=49),
        ]

        # Subject with ELIMINATION (4+ absences) - ALG3
        alg_session = Session.objects.filter(group=group, subject__code='ALG3').first()
        if alg_session:
            for i, past_date in enumerate(past_dates[:5]):  # 5 absences = eliminated
                Attendance.objects.update_or_create(
                    session=alg_session,
                    student=student,
                    date=past_date,
                    defaults={
                        'status': Attendance.Status.ABSENT,
                        'is_justified': i == 0,  # Only 1 justified
                        'justification': 'Certificat médical' if i == 0 else None,
                        'marked_by': teacher
                    }
                )
            self.stdout.write('✗ ALG3: 5 absences (ÉLIMINÉ)')

        # Subject with 2 absences (WARNING) - IA2
        ia_session = Session.objects.filter(group=group, subject__code='IA2').first()
        if ia_session:
            for past_date in past_dates[:2]:  # 2 absences
                Attendance.objects.update_or_create(
                    session=ia_session,
                    student=student,
                    date=past_date,
                    defaults={
                        'status': Attendance.Status.ABSENT,
                        'is_justified': False,
                        'marked_by': teacher
                    }
                )
            # Add some PRESENT records too
            for past_date in past_dates[2:4]:
                Attendance.objects.update_or_create(
                    session=ia_session,
                    student=student,
                    date=past_date,
                    defaults={
                        'status': Attendance.Status.PRESENT,
                        'marked_by': teacher
                    }
                )
            self.stdout.write('⚠ IA2: 2 absences (Avertissement)')

        # Subject with 0 absences - NET2
        net_session = Session.objects.filter(group=group, subject__code='NET2').first()
        if net_session:
            for past_date in past_dates[:4]:
                Attendance.objects.update_or_create(
                    session=net_session,
                    student=student,
                    date=past_date,
                    defaults={
                        'status': Attendance.Status.PRESENT,
                        'marked_by': teacher
                    }
                )
            self.stdout.write('✓ NET2: 0 absences (Bien)')

        # Subject with 1 absence (Late once) - GL2
        gl_session = Session.objects.filter(group=group, subject__code='GL2').first()
        if gl_session:
            Attendance.objects.update_or_create(
                session=gl_session,
                student=student,
                date=past_dates[0],
                defaults={
                    'status': Attendance.Status.LATE,
                    'marked_by': teacher
                }
            )
            for past_date in past_dates[1:3]:
                Attendance.objects.update_or_create(
                    session=gl_session,
                    student=student,
                    date=past_date,
                    defaults={
                        'status': Attendance.Status.PRESENT,
                        'marked_by': teacher
                    }
                )
            self.stdout.write('✓ GL2: 1 retard, présent sinon')

        # Subject FR2 - all present
        fr_session = Session.objects.filter(group=group, subject__code='FR2').first()
        if fr_session:
            for past_date in past_dates[:3]:
                Attendance.objects.update_or_create(
                    session=fr_session,
                    student=student,
                    date=past_date,
                    defaults={
                        'status': Attendance.Status.PRESENT,
                        'marked_by': teacher
                    }
                )
            self.stdout.write('✓ FR2: Toujours présent')

        self.stdout.write(self.style.SUCCESS(f'''
========================================
✅ Data populated for {student.email}
========================================
Password: password123
Group: {group.name}

📊 Résumé des absences:
- ALG3: 5 absences → ÉLIMINÉ ⛔
- IA2: 2 absences → Avertissement ⚠️
- NET2: 0 absences → OK ✅
- GL2: 1 retard → OK ✅
- FR2: 0 absences → OK ✅

Séances aujourd'hui créées pour le jour {today_day}
========================================
        '''))
