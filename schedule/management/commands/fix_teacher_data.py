from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from schedule.models import Session, StudentGroup, StudentGroupMembership

User = get_user_model()

class Command(BaseCommand):
    help = 'Fix teacher data for prof@issat.tn'

    def handle(self, *args, **kwargs):
        try:
            teacher = User.objects.get(email='prof@issat.tn')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Teacher prof@issat.tn not found!'))
            return

        self.stdout.write(f'Teacher: {teacher.email}')
        self.stdout.write(f'  ID: {teacher.id}')
        self.stdout.write(f'  Role: {teacher.role}')
        self.stdout.write(f'  Is Active: {teacher.is_active}')
        
        # Ensure role is correct
        if teacher.role != 'teacher':
            teacher.role = 'teacher'
            teacher.save()
            self.stdout.write(self.style.WARNING(f'  Fixed role to: teacher'))
        
        # Check sessions
        sessions = Session.objects.filter(teacher=teacher)
        self.stdout.write(f'\nSessions linked to this teacher: {sessions.count()}')
        
        if sessions.count() == 0:
            # Link all sessions in 2INFO-A to this teacher
            group = StudentGroup.objects.filter(name='2INFO-A').first()
            if group:
                updated = Session.objects.filter(group=group).update(teacher=teacher)
                self.stdout.write(f'  Linked {updated} sessions from 2INFO-A to teacher')
                sessions = Session.objects.filter(teacher=teacher)
        
        for s in sessions:
            self.stdout.write(f'  - {s.subject.name} ({s.group.name}) Day {s.day_of_week}: {s.start_time}-{s.end_time}')
        
        # Show groups
        groups = StudentGroup.objects.filter(sessions__teacher=teacher).distinct()
        self.stdout.write(f'\nGroups: {groups.count()}')
        for g in groups:
            members = StudentGroupMembership.objects.filter(group=g, is_active=True)
            self.stdout.write(f'  - {g.name}: {members.count()} students')
            for m in members[:5]:
                self.stdout.write(f'      • {m.student.first_name} {m.student.last_name}')
            if members.count() > 5:
                self.stdout.write(f'      ... and {members.count() - 5} more')
        
        self.stdout.write(self.style.SUCCESS('\nDone!'))
