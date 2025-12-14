from django.urls import path
from .views import (
    # Class Management
    ClassListCreateView, ClassDetailView, ClassStudentsView,
    add_student_to_class, remove_student_from_class,

    # Subject Management
    SubjectListCreateView, SubjectDetailView,

    # Timetable Management
    TimetableListCreateView, TimetableDetailView, ClassTimetableView,
    TeacherScheduleView, TeacherTodayScheduleView,
    StudentScheduleView, StudentTodayScheduleView,

    # Attendance Management
    AttendanceListCreateView, AttendanceDetailView, SessionStudentsView,
    MarkAttendanceView, ClassAttendanceView, StudentAttendanceView,
    TeacherSessionsAttendanceView, StudentAttendanceStatsView, ClassAttendanceStatsView,
)

app_name = 'classroom'

urlpatterns = [
    # ==================== CLASS MANAGEMENT ====================
    path('classes/', ClassListCreateView.as_view(), name='class-list-create'),
    path('classes/<int:pk>/', ClassDetailView.as_view(), name='class-detail'),
    path('classes/<int:class_id>/students/', ClassStudentsView.as_view(), name='class-students'),
    path('classes/<int:class_id>/students/add/', add_student_to_class, name='add-student-to-class'),
    path('classes/<int:class_id>/students/<int:student_id>/', remove_student_from_class, name='remove-student-from-class'),

    # ==================== SUBJECT MANAGEMENT ====================
    path('subjects/', SubjectListCreateView.as_view(), name='subject-list-create'),
    path('subjects/<int:pk>/', SubjectDetailView.as_view(), name='subject-detail'),

    # ==================== TIMETABLE MANAGEMENT ====================
    path('timetables/', TimetableListCreateView.as_view(), name='timetable-list-create'),
    path('timetables/<int:pk>/', TimetableDetailView.as_view(), name='timetable-detail'),

    # Admin - Create/Manage Timetables
    path('timetables/class/<int:class_id>/', ClassTimetableView.as_view(), name='class-timetable'),

    # Teacher - View Schedule
    path('timetables/teacher/my-schedule/', TeacherScheduleView.as_view(), name='teacher-schedule'),
    path('timetables/teacher/today/', TeacherTodayScheduleView.as_view(), name='teacher-today-schedule'),
    path('timetables/session/<int:session_id>/', TimetableDetailView.as_view(), name='session-detail'),

    # Student - View Schedule
    path('timetables/student/my-schedule/', StudentScheduleView.as_view(), name='student-schedule'),
    path('timetables/student/today/', StudentTodayScheduleView.as_view(), name='student-today-schedule'),

    # ==================== ATTENDANCE MANAGEMENT ====================
    path('attendance/', AttendanceListCreateView.as_view(), name='attendance-list-create'),
    path('attendance/<int:pk>/', AttendanceDetailView.as_view(), name='attendance-detail'),

    # Teacher - Mark Attendance
    path('attendance/session/<int:session_id>/students/', SessionStudentsView.as_view(), name='session-students'),
    path('attendance/mark/', MarkAttendanceView.as_view(), name='mark-attendance'),

    # View Attendance Records
    path('attendance/class/<int:class_id>/', ClassAttendanceView.as_view(), name='class-attendance'),
    path('attendance/student/<int:student_id>/', StudentAttendanceView.as_view(), name='student-attendance'),
    path('attendance/teacher/my-sessions/', TeacherSessionsAttendanceView.as_view(), name='teacher-sessions-attendance'),

    # Attendance Statistics
    path('attendance/statistics/student/<int:student_id>/', StudentAttendanceStatsView.as_view(), name='student-attendance-stats'),
    path('attendance/statistics/class/<int:class_id>/', ClassAttendanceStatsView.as_view(), name='class-attendance-stats'),
]



