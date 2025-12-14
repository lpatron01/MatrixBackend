from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from schedule.models import StudentGroup, Subject, Session, StudentGroupMembership
from datetime import date, time

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates sessions for today (Sunday) with students for attendance testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test data for teacher attendance testing...')

        # Get or create teacher
        teacher, created = User.objects.get_or_create(
            email='prof@issat.tn',
            defaults={
                'first_name': 'Mohamed',
                'last_name': 'Enseignant',
                'role': User.Role.TEACHER,
                'is_active': True,
                'phone': '98765432',
                'cin': 98765432
            }
        )
        if created:
            teacher.set_password('password123')
            teacher.save()
            self.stdout.write(f'Created teacher: {teacher.email}')
        else:
            self.stdout.write(f'Found teacher: {teacher.email}')

        # Create group 2INFO-A
        group, _ = StudentGroup.objects.get_or_create(
            name='2INFO-A',
            defaults={
                'description': '2ème année Informatique Groupe A',
                'level': 'L2',
                'specialty': 'Informatique'
            }
        )
        self.stdout.write(f'Group: {group.name}')

        # Create subjects
        subjects_data = [
            ('Programmation Web', 'WEB2', 3.0),
            ('Base de Données', 'BD2', 3.0),
            ('Systèmes d\'Exploitation', 'SE2', 2.5),
            ('Mathématiques', 'MATH2', 2.0),
        ]
        
        subjects = {}
        for name, code, coef in subjects_data:
            s, _ = Subject.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'coefficient': coef,
                    'hours_cours': 21,
                    'hours_td': 10,
                    'hours_tp': 20
                }
            )
            subjects[code] = s
        self.stdout.write(f'Subjects created: {len(subjects)}')

        # Create students and add to group
        students_data = [
            ('amal@gmail.com', 'Amal', 'Ben Ahmed', 12345678),
            ('salma@gmail.com', 'Salma', 'Trabelsi', 12345679),
            ('youssef@gmail.com', 'Youssef', 'Mejri', 12345680),
            ('fatma@gmail.com', 'Fatma', 'Bouazizi', 12345681),
            ('ahmed@gmail.com', 'Ahmed', 'Khelifi', 12345682),
            ('nour@gmail.com', 'Nour', 'Sfar', 12345683),
            ('imen@gmail.com', 'Imen', 'Hammami', 12345684),
            ('mehdi@gmail.com', 'Mehdi', 'Belhadj', 12345685),
        ]

        for email, first_name, last_name, cin in students_data:
            student, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': User.Role.STUDENT,
                    'is_active': True,
                    'cin': cin,
                    'phone': str(cin)[:8]
                }
            )
            if created:
                student.set_password('password123')
                student.save()
            
            # Add to group
            StudentGroupMembership.objects.get_or_create(student=student, group=group)

        self.stdout.write(f'Students added to group: {len(students_data)}')

        # Today is Sunday = 0
        # Create sessions happening RIGHT NOW (around current time)
        today_day = 0  # Sunday
        
        # Session 1: Currently in progress (12:00 - 14:00)
        Session.objects.update_or_create(
            group=group,
            day_of_week=today_day,
            start_time=time(12, 0),
            semester='S1',
            academic_year='2024-2025',
            defaults={
                'subject': subjects['WEB2'],
                'end_time': time(14, 0),
                'session_type': Session.SessionType.TD,
                'room': 'Salle A1',
                'teacher': teacher,
                'is_recurring': True
            }
        )
        self.stdout.write('✓ Session 1: Programmation Web TD (12:00-14:00) - EN COURS')

        # Session 2: 14:00 - 16:00
        Session.objects.update_or_create(
            group=group,
            day_of_week=today_day,
            start_time=time(14, 0),
            semester='S1',
            academic_year='2024-2025',
            defaults={
                'subject': subjects['BD2'],
                'end_time': time(16, 0),
                'session_type': Session.SessionType.TP,
                'room': 'Lab 2',
                'teacher': teacher,
                'is_recurring': True
            }
        )
        self.stdout.write('✓ Session 2: Base de Données TP (14:00-16:00)')

        # Session 3: 10:00 - 12:00 (already passed)
        Session.objects.update_or_create(
            group=group,
            day_of_week=today_day,
            start_time=time(10, 0),
            semester='S1',
            academic_year='2024-2025',
            defaults={
                'subject': subjects['MATH2'],
                'end_time': time(12, 0),
                'session_type': Session.SessionType.COURS,
                'room': 'Amphi C',
                'teacher': teacher,
                'is_recurring': True
            }
        )
        self.stdout.write('✓ Session 3: Mathématiques Cours (10:00-12:00) - Terminé')

        self.stdout.write(self.style.SUCCESS(f'''
========================================
✅ Test data created successfully!
========================================
Teacher login: prof@issat.tn / password123

Group: {group.name}
Students: {len(students_data)} étudiants

Sessions today (Sunday):
- 10:00-12:00: Mathématiques (Cours) - Terminé
- 12:00-14:00: Programmation Web (TD) - EN COURS ⭐
- 14:00-16:00: Base de Données (TP) - À venir

The teacher can now mark attendance!
========================================
        '''))
