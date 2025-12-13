from django.urls import path
from . import views

app_name = 'schedule'

urlpatterns = [
    # Student Groups
    path('groups/', views.StudentGroupListCreateView.as_view(), name='group-list'),
    path('groups/<int:pk>/', views.StudentGroupDetailView.as_view(), name='group-detail'),
    
    # Subjects
    path('subjects/', views.SubjectListCreateView.as_view(), name='subject-list'),
    path('subjects/<int:pk>/', views.SubjectDetailView.as_view(), name='subject-detail'),
    
    # Sessions/Schedule
    path('sessions/', views.SessionListCreateView.as_view(), name='session-list'),
    path('sessions/<int:pk>/', views.SessionDetailView.as_view(), name='session-detail'),
    path('my-schedule/', views.MyScheduleView.as_view(), name='my-schedule'),
    
    # Attendance
    path('attendance/', views.AttendanceListView.as_view(), name='attendance-list'),
    path('attendance/mark/', views.MarkAttendanceView.as_view(), name='mark-attendance'),
    path('sessions/<int:session_id>/students/', views.SessionStudentsView.as_view(), name='session-students'),
    
    # Student-specific
    path('my-absences/', views.MyAbsencesView.as_view(), name='my-absences'),
    path('my-group/', views.MyGroupView.as_view(), name='my-group'),
    
    # Group Membership
    path('memberships/', views.StudentGroupMembershipListView.as_view(), name='membership-list'),
    path('memberships/<int:pk>/', views.StudentGroupMembershipDetailView.as_view(), name='membership-detail'),
]
