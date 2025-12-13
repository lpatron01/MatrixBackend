from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Case, When, IntegerField
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from collections import defaultdict

from .models import Class, Subject, Timetable, Attendance
from .serializers import (
    ClassSerializer, ClassDetailSerializer, SubjectSerializer,
    TimetableSerializer, TimetableCreateSerializer, TimetableSessionSerializer,
    AttendanceSerializer, AttendanceCreateSerializer, AttendanceUpdateSerializer,
    StudentAttendanceSerializer, AttendanceStatsSerializer, BulkAttendanceSerializer,
    ClassStudentSerializer
)
from users.models import User


# ==================== CLASS MANAGEMENT VIEWS ====================

class ClassListCreateView(generics.ListCreateAPIView):
    """List all classes or create a new class (Admin only)"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['academic_year', 'is_active']
    search_fields = ['name', 'description']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == User.Role.ADMINISTRATOR:
            return Class.objects.all()
        elif user.role == User.Role.TEACHER:
            # Teachers can see classes they teach
            return Class.objects.filter(
                timetable_entries__teacher=user,
                is_active=True
            ).distinct()
        elif user.role == User.Role.STUDENT:
            # Students can see their classes
            return user.classes.filter(is_active=True)
        return Class.objects.none()

    def get_serializer_class(self):
        return ClassSerializer

    def perform_create(self, serializer):
        serializer.save()


class ClassDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific class"""
    permission_classes = [permissions.IsAuthenticated]
    queryset = Class.objects.all()
    serializer_class = ClassDetailSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == User.Role.ADMINISTRATOR:
            return Class.objects.all()
        elif user.role == User.Role.TEACHER:
            return Class.objects.filter(timetable_entries__teacher=user).distinct()
        elif user.role == User.Role.STUDENT:
            return user.classes.all()
        return Class.objects.none()


class ClassStudentsView(generics.RetrieveAPIView):
    """Get students in a specific class"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ClassStudentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == User.Role.ADMINISTRATOR:
            return Class.objects.all()
        elif user.role == User.Role.TEACHER:
            return Class.objects.filter(timetable_entries__teacher=user).distinct()
        return Class.objects.none()

    def get(self, request, *args, **kwargs):
        class_obj = self.get_object()
        students = class_obj.students.all()
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_student_to_class(request, class_id):
    """Add a student to a class (Admin/Teacher only)"""
    if request.user.role not in [User.Role.ADMINISTRATOR] and not request.user.is_staff:
        return Response(
            {"error": "Only administrators can manage class enrollment"},
            status=status.HTTP_403_FORBIDDEN
        )

    class_obj = get_object_or_404(Class, id=class_id)
    student_id = request.data.get('student_id')

    if not student_id:
        return Response(
            {"error": "student_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    student = get_object_or_404(User, id=student_id, role=User.Role.STUDENT)
    class_obj.students.add(student)

    return Response({"message": f"Student {student.get_full_name()} added to class {class_obj.name}"})


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_student_from_class(request, class_id, student_id):
    """Remove a student from a class (Admin only)"""
    if not request.user.is_staff and request.user.role != User.Role.ADMINISTRATOR:
        return Response(
            {"error": "Only administrators can manage class enrollment"},
            status=status.HTTP_403_FORBIDDEN
        )

    class_obj = get_object_or_404(Class, id=class_id)
    student = get_object_or_404(User, id=student_id, role=User.Role.STUDENT)

    class_obj.students.remove(student)
    return Response({"message": f"Student {student.get_full_name()} removed from class {class_obj.name}"})


# ==================== SUBJECT MANAGEMENT VIEWS ====================

class SubjectListCreateView(generics.ListCreateAPIView):
    """List all subjects or create a new subject (Admin only)"""
    permission_classes = [permissions.IsAuthenticated]
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code']

    def perform_create(self, serializer):
        if not self.request.user.is_staff and self.request.user.role != User.Role.ADMINISTRATOR:
            raise permissions.PermissionDenied("Only administrators can create subjects")
        serializer.save()


class SubjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific subject"""
    permission_classes = [permissions.IsAuthenticated]
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


# ==================== TIMETABLE MANAGEMENT VIEWS ====================

class TimetableListCreateView(generics.ListCreateAPIView):
    """List all timetable entries or create a new one (Admin only)"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['class_room', 'subject', 'teacher', 'day_of_week', 'time_slot', 'academic_year', 'is_active']
    search_fields = ['class_room__name', 'subject__name', 'teacher__email']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == User.Role.ADMINISTRATOR:
            return Timetable.objects.all()
        elif user.role == User.Role.TEACHER:
            return Timetable.objects.filter(teacher=user)
        elif user.role == User.Role.STUDENT:
            return Timetable.objects.filter(class_room__students=user)
        return Timetable.objects.none()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TimetableCreateSerializer
        return TimetableSerializer

    def perform_create(self, serializer):
        if not self.request.user.is_staff and self.request.user.role != User.Role.ADMINISTRATOR:
            raise permissions.PermissionDenied("Only administrators can create timetable entries")
        serializer.save()


class TimetableDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific timetable entry"""
    permission_classes = [permissions.IsAuthenticated]
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == User.Role.ADMINISTRATOR:
            return Timetable.objects.all()
        elif user.role == User.Role.TEACHER:
            return Timetable.objects.filter(teacher=user)
        return Timetable.objects.none()


class ClassTimetableView(generics.ListAPIView):
    """Get weekly timetable for a specific class"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TimetableSerializer

    def get_queryset(self):
        class_id = self.kwargs['class_id']
        user = self.request.user

        # Check permissions
        if user.role == User.Role.STUDENT and not user.classes.filter(id=class_id).exists():
            return Timetable.objects.none()
        elif user.role == User.Role.TEACHER and not Timetable.objects.filter(
            class_room_id=class_id, teacher=user
        ).exists() and not user.is_staff and user.role != User.Role.ADMINISTRATOR:
            return Timetable.objects.none()

        return Timetable.objects.filter(
            class_room_id=class_id,
            is_active=True
        ).order_by('day_of_week', 'time_slot')


class TeacherScheduleView(APIView):
    """Get logged-in teacher's schedule"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != User.Role.TEACHER:
            return Response(
                {"error": "Only teachers can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN
            )

        today = request.query_params.get('date')
        if today:
            try:
                today = datetime.strptime(today, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            today = timezone.now().date()

        # Get today's sessions
        day_name = today.strftime('%A').lower()
        timetable_entries = Timetable.objects.filter(
            teacher=request.user,
            day_of_week=day_name,
            is_active=True
        ).order_by('time_slot')

        serializer = TimetableSerializer(timetable_entries, many=True)
        return Response(serializer.data)


class TeacherTodayScheduleView(APIView):
    """Get today's sessions for logged-in teacher"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != User.Role.TEACHER:
            return Response(
                {"error": "Only teachers can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN
            )

        today = timezone.now().date()
        day_name = today.strftime('%A').lower()

        timetable_entries = Timetable.objects.filter(
            teacher=request.user,
            day_of_week=day_name,
            is_active=True
        ).order_by('time_slot')

        serializer = TimetableSessionSerializer(timetable_entries, many=True)
        return Response(serializer.data)


class StudentScheduleView(APIView):
    """Get logged-in student's timetable"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != User.Role.STUDENT:
            return Response(
                {"error": "Only students can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN
            )

        timetable_entries = Timetable.objects.filter(
            class_room__students=request.user,
            is_active=True
        ).order_by('day_of_week', 'time_slot')

        serializer = TimetableSerializer(timetable_entries, many=True)
        return Response(serializer.data)


class StudentTodayScheduleView(APIView):
    """Get today's schedule for logged-in student"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != User.Role.STUDENT:
            return Response(
                {"error": "Only students can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN
            )

        today = timezone.now().date()
        day_name = today.strftime('%A').lower()

        timetable_entries = Timetable.objects.filter(
            class_room__students=request.user,
            day_of_week=day_name,
            is_active=True
        ).order_by('time_slot')

        serializer = TimetableSerializer(timetable_entries, many=True)
        return Response(serializer.data)


# ==================== ATTENDANCE MANAGEMENT VIEWS ====================

class AttendanceListCreateView(generics.ListCreateAPIView):
    """List all attendance records or create a new one"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'timetable_entry', 'date', 'status']
    ordering_fields = ['date', 'created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == User.Role.ADMINISTRATOR:
            return Attendance.objects.all()
        elif user.role == User.Role.TEACHER:
            return Attendance.objects.filter(timetable_entry__teacher=user)
        elif user.role == User.Role.STUDENT:
            return Attendance.objects.filter(student=user)
        return Attendance.objects.none()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AttendanceCreateSerializer
        return AttendanceSerializer


class AttendanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific attendance record"""
    permission_classes = [permissions.IsAuthenticated]
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == User.Role.ADMINISTRATOR:
            return Attendance.objects.all()
        elif user.role == User.Role.TEACHER:
            return Attendance.objects.filter(timetable_entry__teacher=user)
        return Attendance.objects.none()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AttendanceUpdateSerializer
        return AttendanceSerializer


class SessionStudentsView(APIView):
    """Get student list for a specific session (for attendance marking)"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, session_id):
        timetable_entry = get_object_or_404(Timetable, id=session_id)

        # Check permissions
        if (request.user.role != User.Role.TEACHER or timetable_entry.teacher != request.user) and \
           not request.user.is_staff and request.user.role != User.Role.ADMINISTRATOR:
            return Response(
                {"error": "You can only view students for your own sessions"},
                status=status.HTTP_403_FORBIDDEN
            )

        students = timetable_entry.class_room.students.all()
        serializer = ClassStudentSerializer(students, many=True)

        return Response({
            'session': TimetableSessionSerializer(timetable_entry).data,
            'students': serializer.data
        })


class MarkAttendanceView(APIView):
    """Mark attendance for multiple students in a session"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = BulkAttendanceSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        timetable_entry_id = serializer.validated_data['timetable_entry_id']
        date = serializer.validated_data['date']
        attendances_data = serializer.validated_data['attendances']

        timetable_entry = get_object_or_404(Timetable, id=timetable_entry_id)

        # Check permissions
        if (request.user.role != User.Role.TEACHER or timetable_entry.teacher != request.user) and \
           not request.user.is_staff and request.user.role != User.Role.ADMINISTRATOR:
            return Response(
                {"error": "You can only mark attendance for your own sessions"},
                status=status.HTTP_403_FORBIDDEN
            )

        created_records = []
        updated_records = []

        for attendance_data in attendances_data:
            student_id = attendance_data.get('student_id')
            status_val = attendance_data.get('status')
            remarks = attendance_data.get('remarks', '')

            if not student_id or not status_val:
                continue

            student = get_object_or_404(User, id=student_id, role=User.Role.STUDENT)

            # Check if attendance record already exists
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                timetable_entry=timetable_entry,
                date=date,
                defaults={
                    'status': status_val,
                    'remarks': remarks,
                    'marked_by': request.user
                }
            )

            if created:
                created_records.append(attendance)
            else:
                attendance.status = status_val
                attendance.remarks = remarks
                attendance.marked_by = request.user
                attendance.save()
                updated_records.append(attendance)

        return Response({
            'message': f'Created {len(created_records)} and updated {len(updated_records)} attendance records',
            'created': AttendanceSerializer(created_records, many=True).data,
            'updated': AttendanceSerializer(updated_records, many=True).data
        })


class ClassAttendanceView(generics.ListAPIView):
    """Get attendance records for a specific class"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        class_id = self.kwargs['class_id']
        user = self.request.user

        # Check permissions
        if user.role == User.Role.STUDENT and not user.classes.filter(id=class_id).exists():
            return Attendance.objects.none()
        elif user.role == User.Role.TEACHER and not Timetable.objects.filter(
            class_room_id=class_id, teacher=user
        ).exists() and not user.is_staff and user.role != User.Role.ADMINISTRATOR:
            return Attendance.objects.none()

        queryset = Attendance.objects.filter(timetable_entry__class_room_id=class_id)

        # Apply filters
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        date = self.request.query_params.get('date')
        status_filter = self.request.query_params.get('status')
        session = self.request.query_params.get('session')

        if date:
            queryset = queryset.filter(date=date)
        elif date_from and date_to:
            queryset = queryset.filter(date__range=[date_from, date_to])
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if session:
            queryset = queryset.filter(timetable_entry__time_slot=session)

        return queryset.order_by('-date', 'timetable_entry__time_slot')


class StudentAttendanceView(generics.ListAPIView):
    """Get attendance history for a specific student"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StudentAttendanceSerializer

    def get_queryset(self):
        student_id = self.kwargs['student_id']
        user = self.request.user

        # Check permissions
        if user.role == User.Role.STUDENT and user.id != int(student_id):
            return Attendance.objects.none()
        elif user.role == User.Role.TEACHER:
            # Teachers can only see attendance for students in their classes
            student_classes = Class.objects.filter(
                students__id=student_id,
                timetable_entries__teacher=user
            ).distinct()
            if not student_classes.exists():
                return Attendance.objects.none()

        queryset = Attendance.objects.filter(student_id=student_id)

        # Apply filters
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        date = self.request.query_params.get('date')

        if date:
            queryset = queryset.filter(date=date)
        elif date_from and date_to:
            queryset = queryset.filter(date__range=[date_from, date_to])

        return queryset.order_by('-date')


class TeacherSessionsAttendanceView(generics.ListAPIView):
    """Get attendance records for teacher's sessions"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        if self.request.user.role != User.Role.TEACHER:
            return Attendance.objects.none()

        queryset = Attendance.objects.filter(timetable_entry__teacher=self.request.user)

        # Apply filters
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        date = self.request.query_params.get('date')
        class_id = self.request.query_params.get('class_id')

        if date:
            queryset = queryset.filter(date=date)
        elif date_from and date_to:
            queryset = queryset.filter(date__range=[date_from, date_to])
        if class_id:
            queryset = queryset.filter(timetable_entry__class_room_id=class_id)

        return queryset.order_by('-date', 'timetable_entry__time_slot')


class StudentAttendanceStatsView(APIView):
    """Get attendance statistics for a specific student"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, student_id):
        user = request.user

        # Check permissions
        if user.role == User.Role.STUDENT and user.id != int(student_id):
            return Response(
                {"error": "You can only view your own attendance statistics"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get date range
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        queryset = Attendance.objects.filter(student_id=student_id)

        if date_from and date_to:
            queryset = queryset.filter(date__range=[date_from, date_to])

        # Calculate statistics
        stats = queryset.aggregate(
            total_sessions=Count('id'),
            present_count=Count(Case(When(status='present', then=1), output_field=IntegerField())),
            absent_count=Count(Case(When(status='absent', then=1), output_field=IntegerField())),
            late_count=Count(Case(When(status='late', then=1), output_field=IntegerField())),
            excused_count=Count(Case(When(status='excused', then=1), output_field=IntegerField())),
        )

        total_sessions = stats['total_sessions']
        attendance_percentage = (stats['present_count'] / total_sessions * 100) if total_sessions > 0 else 0

        stats_data = {
            'total_sessions': total_sessions,
            'present_count': stats['present_count'],
            'absent_count': stats['absent_count'],
            'late_count': stats['late_count'],
            'excused_count': stats['excused_count'],
            'attendance_percentage': round(attendance_percentage, 2)
        }

        serializer = AttendanceStatsSerializer(stats_data)
        return Response(serializer.data)


class ClassAttendanceStatsView(APIView):
    """Get attendance statistics for a specific class"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, class_id):
        user = request.user

        # Check permissions
        if user.role == User.Role.STUDENT and not user.classes.filter(id=class_id).exists():
            return Response(
                {"error": "You can only view statistics for your own classes"},
                status=status.HTTP_403_FORBIDDEN
            )
        elif user.role == User.Role.TEACHER and not Timetable.objects.filter(
            class_room_id=class_id, teacher=user
        ).exists() and not user.is_staff and user.role != User.Role.ADMINISTRATOR:
            return Response(
                {"error": "You can only view statistics for classes you teach"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get date range
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        queryset = Attendance.objects.filter(timetable_entry__class_room_id=class_id)

        if date_from and date_to:
            queryset = queryset.filter(date__range=[date_from, date_to])

        # Calculate statistics
        stats = queryset.aggregate(
            total_sessions=Count('id'),
            present_count=Count(Case(When(status='present', then=1), output_field=IntegerField())),
            absent_count=Count(Case(When(status='absent', then=1), output_field=IntegerField())),
            late_count=Count(Case(When(status='late', then=1), output_field=IntegerField())),
            excused_count=Count(Case(When(status='excused', then=1), output_field=IntegerField())),
        )

        total_sessions = stats['total_sessions']
        attendance_percentage = (stats['present_count'] / total_sessions * 100) if total_sessions > 0 else 0

        stats_data = {
            'total_sessions': total_sessions,
            'present_count': stats['present_count'],
            'absent_count': stats['absent_count'],
            'late_count': stats['late_count'],
            'excused_count': stats['excused_count'],
            'attendance_percentage': round(attendance_percentage, 2)
        }

        serializer = AttendanceStatsSerializer(stats_data)
        return Response(serializer.data)