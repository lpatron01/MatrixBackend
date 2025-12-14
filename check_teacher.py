import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from schedule.models import Session
from users.models import User

t = User.objects.get(email='prof@issat.tn')
sessions = Session.objects.filter(teacher=t)
print(f'Teacher ID: {t.id}')
print(f'Sessions for teacher: {sessions.count()}')
for s in sessions:
    print(f'  - {s.subject.name} ({s.group.name}) - Day {s.day_of_week}')

# Check unique groups
groups = set(s.group for s in sessions)
print(f'\nUnique groups: {len(groups)}')
for g in groups:
    print(f'  - {g.name}: {g.students.count()} students')
