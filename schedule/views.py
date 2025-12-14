from django.db.models import Count, Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import date, timedelta

from .models import StudentGroup, Subject, Session, Attendance, StudentGroupMembership
from .serializers import (
    StudentGroupSerializer, SubjectSerializer, SessionSerializer, SessionListSerializer,
    AttendanceSerializer, AttendanceCreateSerializer, BulkAttendanceSerializer,
    StudentGroupMembershipSerializer, StudentAbsencesSummarySerializer
)


class IsAdminUser(permissions.BasePermission):
    """Custom permission for admin users"""
    def has_permission(self, request, view):
        return request.user and request.user.role in ['administrator', 'admin']


class IsTeacherOrAdmin(permissions.BasePermission):
    """Permission for teachers or admins"""
    def has_permission(self, request, view):
        return request.user and request.user.role in ['teacher', 'administrator', 'admin']


# =============================================================================
# Student Group Views
# =============================================================================

class StudentGroupListCreateView(generics.ListCreateAPIView):
    """
    GET: List all student groups
    POST: Create a new group (admin only)
    """
    queryset = StudentGroup.objects.all()
    serializer_class = StudentGroupSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]


class StudentGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/PATCH/DELETE: Manage a specific group
    """
    queryset = StudentGroup.objects.all()
    serializer_class = StudentGroupSerializer
    permission_classes = [IsAdminUser]


# =============================================================================
# Subject Views
# =============================================================================

class SubjectListCreateView(generics.ListCreateAPIView):
    """
    GET: List all subjects
    POST: Create a new subject (admin only)
    """
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]


class SubjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Manage a specific subject"""
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAdminUser]


# =============================================================================
# Session/Schedule Views
# =============================================================================

class SessionListCreateView(generics.ListCreateAPIView):
    """
    GET: List sessions (filtered by role)
    POST: Create a session (admin only)
    """
    serializer_class = SessionListSerializer

    def get_queryset(self):
        queryset = Session.objects.filter(is_active=True)
        user = self.request.user

        # Filter by role
        if user.role == 'student':
            # Get student's groups
            group_ids = StudentGroupMembership.objects.filter(
                student=user, is_active=True
            ).values_list('group_id', flat=True)
            queryset = queryset.filter(group_id__in=group_ids)
        elif user.role == 'teacher':
            queryset = queryset.filter(teacher=user)

        # Additional filters
        day = self.request.query_params.get('day')
        if day:
            queryset = queryset.filter(day_of_week=day)

        group_id = self.request.query_params.get('group')
        if group_id:
            queryset = queryset.filter(group_id=group_id)

        session_type = self.request.query_params.get('type')
        if session_type:
            queryset = queryset.filter(session_type=session_type)

        semester = self.request.query_params.get('semester')
        if semester:
            queryset = queryset.filter(semester=semester)

        return queryset.select_related('subject', 'teacher', 'group')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SessionSerializer
        return SessionListSerializer


class SessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Manage a specific session"""
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsAdminUser]


class MyScheduleView(APIView):
    """Get current user's weekly schedule"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        queryset = Session.objects.filter(is_active=True)

        if user.role == 'student':
            group_ids = StudentGroupMembership.objects.filter(
                student=user, is_active=True
            ).values_list('group_id', flat=True)
            queryset = queryset.filter(group_id__in=group_ids)
        elif user.role == 'teacher':
            queryset = queryset.filter(teacher=user)

        # Organize by day
        schedule = {}
        for day in range(1, 7):  # Monday to Saturday
            day_sessions = queryset.filter(day_of_week=day).select_related('subject', 'teacher', 'group')
            schedule[day] = SessionListSerializer(day_sessions, many=True).data

        return Response(schedule)


# =============================================================================
# Attendance Views
# =============================================================================

class AttendanceListView(generics.ListAPIView):
    """
    List attendance records
    - Students see their own attendance
    - Teachers see attendance for their sessions
    - Admins see all
    """
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Attendance.objects.all()

        if user.role == 'student':
            queryset = queryset.filter(student=user)
        elif user.role == 'teacher':
            queryset = queryset.filter(session__teacher=user)

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        # Filter by status
        attendance_status = self.request.query_params.get('status')
        if attendance_status:
            queryset = queryset.filter(status=attendance_status)

        # Filter by session
        session_id = self.request.query_params.get('session')
        if session_id:
            queryset = queryset.filter(session_id=session_id)

        return queryset.select_related('session', 'student', 'marked_by')


class MarkAttendanceView(APIView):
    """Mark attendance for a session (Teachers only)"""
    permission_classes = [IsTeacherOrAdmin]

    def post(self, request):
        serializer = BulkAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_id = serializer.validated_data['session_id']
        attendance_date = serializer.validated_data['date']
        attendances = serializer.validated_data['attendances']

        # Verify session exists and belongs to teacher
        try:
            session = Session.objects.get(id=session_id)
            if request.user.role == 'teacher' and session.teacher != request.user:
                return Response(
                    {'detail': 'You can only mark attendance for your own sessions'},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Session.DoesNotExist:
            return Response({'detail': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        created = []
        updated = []

        for att in attendances:
            student_id = att['student_id']
            att_status = att['status']

            attendance, is_created = Attendance.objects.update_or_create(
                session_id=session_id,
                student_id=student_id,
                date=attendance_date,
                defaults={
                    'status': att_status,
                    'marked_by': request.user
                }
            )

            if is_created:
                created.append(student_id)
            else:
                updated.append(student_id)

        return Response({
            'message': 'Attendance marked successfully',
            'created': len(created),
            'updated': len(updated)
        })


class MyAbsencesView(APIView):
    """Get current student's absences summary"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        
        if user.role != 'student':
            return Response(
                {'detail': 'Only students can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get all attendance records
        attendances = Attendance.objects.filter(student=user).select_related('session', 'session__subject')
        
        # Get total sessions for student's groups
        group_ids = StudentGroupMembership.objects.filter(
            student=user, is_active=True
        ).values_list('group_id', flat=True)
        
        total_sessions = Session.objects.filter(group_id__in=group_ids, is_active=True).count()

        # Calculate statistics
        absences = attendances.filter(status__in=['ABSENT', 'LATE'])
        total_absences = absences.count()
        justified = absences.filter(is_justified=True).count()
        unjustified = total_absences - justified

        # Presence rate
        presence_count = attendances.filter(status='PRESENT').count()
        total_marked = attendances.count()
        presence_rate = (presence_count / total_marked * 100) if total_marked > 0 else 100

        data = {
            'total_sessions': total_sessions,
            'total_absences': total_absences,
            'justified_absences': justified,
            'unjustified_absences': unjustified,
            'presence_rate': round(presence_rate, 2),
            'absences': AttendanceSerializer(absences, many=True).data
        }

        return Response(data)


class SessionStudentsView(APIView):
    """Get list of students for a session (for taking attendance)"""
    permission_classes = [IsTeacherOrAdmin]

    def get(self, request, session_id):
        try:
            session = Session.objects.get(id=session_id)
        except Session.DoesNotExist:
            return Response({'detail': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check permission for teachers
        if request.user.role == 'teacher' and session.teacher != request.user:
            return Response(
                {'detail': 'You can only view students for your own sessions'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get students in the session's group
        students = StudentGroupMembership.objects.filter(
            group=session.group,
            is_active=True
        ).select_related('student')

        # Get attendance for today
        today = request.query_params.get('date', date.today())
        
        student_data = []
        for membership in students:
            student = membership.student
            attendance = Attendance.objects.filter(
                session=session,
                student=student,
                date=today
            ).first()

            student_data.append({
                'id': student.id,
                'email': student.email,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'attendance_status': attendance.status if attendance else None,
                'is_justified': attendance.is_justified if attendance else False
            })

        return Response({
            'session': SessionListSerializer(session).data,
            'date': today,
            'students': student_data
        })


# =============================================================================
# Group Membership Views
# =============================================================================

class StudentGroupMembershipListView(generics.ListCreateAPIView):
    """List/Create group memberships (admin only)"""
    serializer_class = StudentGroupMembershipSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = StudentGroupMembership.objects.all()
        
        group_id = self.request.query_params.get('group')
        if group_id:
            queryset = queryset.filter(group_id=group_id)

        return queryset.select_related('student', 'group')


class StudentGroupMembershipDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Manage a specific membership"""
    queryset = StudentGroupMembership.objects.all()
    serializer_class = StudentGroupMembershipSerializer
    permission_classes = [IsAdminUser]


class MyGroupView(APIView):
    """Get current student's group"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != 'student':
            return Response({'detail': 'Only for students'}, status=status.HTTP_403_FORBIDDEN)

        memberships = StudentGroupMembership.objects.filter(
            student=request.user,
            is_active=True
        ).select_related('group')

        groups = [StudentGroupSerializer(m.group).data for m in memberships]
        return Response(groups)
