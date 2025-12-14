from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from schedule.models import Session, StudentGroup

User = get_user_model()

class Command(BaseCommand):
    help = 'Check teacher sessions and link groups'

    def handle(self, *args, **kwargs):
        teacher = User.objects.get(email='prof@issat.tn')
        self.stdout.write(f'Teacher: {teacher.email} (ID: {teacher.id})')
        
        sessions = Session.objects.filter(teacher=teacher)
        self.stdout.write(f'Sessions: {sessions.count()}')
        for s in sessions:
            self.stdout.write(f'  - {s.subject.name} ({s.group.name}) - Day {s.day_of_week}')
        
        groups = StudentGroup.objects.filter(sessions__teacher=teacher).distinct()
        self.stdout.write(f'\nGroups where teacher has sessions: {groups.count()}')
        for g in groups:
            self.stdout.write(f'  - {g.name}: {g.students.count()} students')
