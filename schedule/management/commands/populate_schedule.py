from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from schedule.models import StudentGroup, Subject, Session, StudentGroupMembership, Attendance
from datetime import time, date, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with test data for Schedule app'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test data...')

        # 1. Create Teachers
        teachers = []
        for i in range(1, 4):
            email = f'teacher{i}@issat.tn'
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': f'Enseignant',
                    'last_name': f'{i}',
                    'role': User.Role.TEACHER,
                    'is_active': True
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            teachers.append(user)
        self.stdout.write(f'Teachers created/found: {len(teachers)}')

        # 2. Create Students
        students = []
        for i in range(1, 21):
            email = f'student{i}@issat.tn'
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': f'Etudiant',
                    'last_name': f'{i}',
                    'role': User.Role.STUDENT,
                    'is_active': True
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            students.append(user)
        self.stdout.write(f'Students created/found: {len(students)}')

        # 3. Create Groups
        group_a, _ = StudentGroup.objects.get_or_create(
            name='2INFO-A',
            defaults={
                'description': '2ème année Informatique Groupe A',
                'level': 'L2',
                'specialty': 'Informatique'
            }
        )
        group_b, _ = StudentGroup.objects.get_or_create(
            name='2INFO-B',
            defaults={
                'description': '2ème année Informatique Groupe B',
                'level': 'L2',
                'specialty': 'Informatique'
            }
        )
        self.stdout.write(f'Groups created: {group_a.name}, {group_b.name}')

        # 4. Assign Students to Groups
        for i, student in enumerate(students):
            group = group_a if i < 10 else group_b
            StudentGroupMembership.objects.get_or_create(
                student=student,
                group=group
            )
        self.stdout.write('Students assigned to groups')

        # 5. Create Subjects
        subjects_data = [
            {'name': 'Développement Web', 'code': 'WEB2', 'coef': 3.0, 'h_c': 21, 'h_td': 10, 'h_tp': 20},
            {'name': 'Systèmes d\'Exploitation', 'code': 'OS2', 'coef': 2.0, 'h_c': 21, 'h_td': 10, 'h_tp': 10},
            {'name': 'Base de Données', 'code': 'BD2', 'coef': 3.0, 'h_c': 21, 'h_td': 10, 'h_tp': 20},
            {'name': 'Probabilités et Stats', 'code': 'MATH2', 'coef': 2.0, 'h_c': 21, 'h_td': 21, 'h_tp': 0},
            {'name': 'Anglais', 'code': 'ENG2', 'coef': 1.0, 'h_c': 0, 'h_td': 21, 'h_tp': 0},
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

        # 6. Create Sessions (Weekly Schedule)
        # 2INFO-A Schedule
        sessions_data_a = [
            (Session.DayOfWeek.MONDAY, '08:30:00', '10:00:00', 'WEB2', Session.SessionType.COURS, 'Amphi A', teachers[0]),
            (Session.DayOfWeek.MONDAY, '10:15:00', '11:45:00', 'WEB2', Session.SessionType.TP, 'Lab 1', teachers[0]),
            (Session.DayOfWeek.TUESDAY, '08:30:00', '10:00:00', 'BD2', Session.SessionType.COURS, 'Salle 12', teachers[1]),
            (Session.DayOfWeek.WEDNESDAY, '14:00:00', '15:30:00', 'OS2', Session.SessionType.COURS, 'Amphi B', teachers[2]),
        ]

        # 2INFO-B Schedule
        sessions_data_b = [
            (Session.DayOfWeek.MONDAY, '14:00:00', '15:30:00', 'WEB2', Session.SessionType.TP, 'Lab 2', teachers[0]),
            (Session.DayOfWeek.TUESDAY, '10:15:00', '11:45:00', 'BD2', Session.SessionType.COURS, 'Salle 12', teachers[1]),
            (Session.DayOfWeek.THURSDAY, '08:30:00', '10:00:00', 'MATH2', Session.SessionType.TD, 'Salle 05', teachers[2]),
        ]

        def create_sessions(group, data):
            for day, start, end, sub_code, type_, room, teacher in data:
                Session.objects.get_or_create(
                    group=group,
                    day_of_week=day,
                    start_time=start,
                    subject=subjects[sub_code],
                    defaults={
                        'end_time': end,
                        'session_type': type_,
                        'room': room,
                        'teacher': teacher,
                        'semester': 'S1',
                        'academic_year': '2024-2025'
                    }
                )

        create_sessions(group_a, sessions_data_a)
        create_sessions(group_b, sessions_data_b)
        self.stdout.write('Sessions created')

        # 7. Create Attendance Records (Last week)
        today = date.today()
        # Find a session from last week (e.g., Monday)
        last_monday = today - timedelta(days=today.weekday() + 7)
        
        # Get 'WEB2' TP session for Group A on Monday
        session_tp_a = Session.objects.filter(
            group=group_a, 
            subject__code='WEB2', 
            session_type=Session.SessionType.TP
        ).first()

        if session_tp_a:
            students_grp_a = StudentGroupMembership.objects.filter(group=group_a).values_list('student', flat=True)
            for student_id in students_grp_a:
                # Random status
                status = random.choice([Attendance.Status.PRESENT, Attendance.Status.PRESENT, Attendance.Status.PRESENT, Attendance.Status.ABSENT])
                Attendance.objects.get_or_create(
                    session=session_tp_a,
                    student_id=student_id,
                    date=last_monday,
                    defaults={
                        'status': status,
                        'marked_by': session_tp_a.teacher
                    }
                )
            self.stdout.write('Attendance records created for one session')

        self.stdout.write(self.style.SUCCESS('Successfully populated schedule data'))
