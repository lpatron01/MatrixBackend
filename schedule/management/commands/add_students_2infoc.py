from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from schedule.models import StudentGroup, StudentGroupMembership

User = get_user_model()

class Command(BaseCommand):
    help = 'Add students to group 2INFO-C for teacher prof@issat.tn'

    def handle(self, *args, **kwargs):
        # Get the group 2INFO-C
        group = StudentGroup.objects.get(name='2INFO-C')
        self.stdout.write(f'Group: {group.name}')

        # Students to add
        students_data = [
            ('salma.trabelsi@gmail.com', 'Salma', 'Trabelsi', 11111111),
            ('youssef.mejri@gmail.com', 'Youssef', 'Mejri', 22222222),
            ('fatima.bouazizi@gmail.com', 'Fatima', 'Bouazizi', 33333333),
            ('ahmed.khelifi@gmail.com', 'Ahmed', 'Khelifi', 44444444),
            ('nour.sfar@gmail.com', 'Nour', 'Sfar', 55555555),
            ('imen.hammami@gmail.com', 'Imen', 'Hammami', 66666666),
            ('mehdi.belhadj@gmail.com', 'Mehdi', 'Belhadj', 77777777),
        ]

        for email, first_name, last_name, cin in students_data:
            student, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': 'student',
                    'is_active': True,
                    'cin': cin,
                    'phone': str(cin)[:8]
                }
            )
            if created:
                student.set_password('password123')
                student.save()
            
            membership, m_created = StudentGroupMembership.objects.get_or_create(
                student=student, 
                group=group
            )
            status = 'NEW' if m_created else 'exists'
            self.stdout.write(f'  {first_name} {last_name}: {status}')

        total = StudentGroupMembership.objects.filter(group=group, is_active=True).count()
        self.stdout.write(self.style.SUCCESS(f'\nTotal students in {group.name}: {total}'))
