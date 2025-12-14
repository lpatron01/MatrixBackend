from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Club, ClubEvent, ClubReport, ClubAnnouncement
from .serializers import (
    ClubSerializer, ClubCreateSerializer, ClubUpdateSerializer,
    ClubEventSerializer, ClubEventCreateSerializer,
    ClubReportSerializer, ClubReportCreateSerializer,
    ClubAnnouncementSerializer, ClubAnnouncementCreateSerializer
)


class IsClubManager(permissions.BasePermission):
    """Permission for club managers"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'club_manager'


class IsAdminOrReadOnly(permissions.BasePermission):
    """Admin can write, others can read"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role in ['administrator', 'scolar_administrator']


# ============================================================================
# Club Views
# ============================================================================

class ClubListCreateView(generics.ListCreateAPIView):
    """List all clubs or create a new club"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'club_manager':
            return Club.objects.filter(president=user)
        elif user.role in ['administrator', 'scolar_administrator']:
            return Club.objects.all()
        return Club.objects.filter(status='active')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ClubCreateSerializer
        return ClubSerializer

    def perform_create(self, serializer):
        serializer.save(president=self.request.user)


class ClubDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a club"""
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'public_id'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'club_manager':
            return Club.objects.filter(president=user)
        elif user.role in ['administrator', 'scolar_administrator']:
            return Club.objects.all()
        return Club.objects.filter(status='active')

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ClubUpdateSerializer
        return ClubSerializer


class ClubApproveView(generics.UpdateAPIView):
    """Approve or reject a club"""
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = ClubUpdateSerializer
    lookup_field = 'public_id'
    queryset = Club.objects.all()

    def perform_update(self, serializer):
        serializer.save()


# ============================================================================
# Club Event Views
# ============================================================================

class ClubEventListCreateView(generics.ListCreateAPIView):
    """List all events or create a new event"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'club']
    ordering_fields = ['date', 'created_at']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'club_manager':
            return ClubEvent.objects.filter(club__president=user)
        elif user.role in ['administrator', 'scolar_administrator']:
            return ClubEvent.objects.all()
        return ClubEvent.objects.filter(status='approved')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ClubEventCreateSerializer
        return ClubEventSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ClubEventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an event"""
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'public_id'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'club_manager':
            return ClubEvent.objects.filter(club__president=user)
        elif user.role in ['administrator', 'scolar_administrator']:
            return ClubEvent.objects.all()
        return ClubEvent.objects.filter(status='approved')

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ClubEventCreateSerializer
        return ClubEventSerializer


# ============================================================================
# Club Report Views
# ============================================================================

class ClubReportListCreateView(generics.ListCreateAPIView):
    """List all reports or create a new report"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['semester', 'academic_year', 'club']
    ordering_fields = ['created_at']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'club_manager':
            return ClubReport.objects.filter(club__president=user)
        elif user.role in ['administrator', 'scolar_administrator']:
            return ClubReport.objects.all()
        return ClubReport.objects.none()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ClubReportCreateSerializer
        return ClubReportSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ClubReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a report"""
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'public_id'
    serializer_class = ClubReportSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'club_manager':
            return ClubReport.objects.filter(club__president=user)
        return ClubReport.objects.all()


# ============================================================================
# Club Announcement Views
# ============================================================================

class ClubAnnouncementListCreateView(generics.ListCreateAPIView):
    """List announcements or create new (admin only)"""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'priority']

    def get_queryset(self):
        user = self.request.user
        queryset = ClubAnnouncement.objects.filter(is_active=True)
        
        # Filter expired announcements
        queryset = queryset.filter(
            models.Q(expires_at__isnull=True) | 
            models.Q(expires_at__gte=timezone.now())
        )
        
        if user.role == 'club_manager':
            # Get announcements for manager's clubs or global
            clubs = Club.objects.filter(president=user)
            return queryset.filter(
                models.Q(is_global=True) | 
                models.Q(target_clubs__in=clubs)
            ).distinct()
        
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ClubAnnouncementCreateSerializer
        return ClubAnnouncementSerializer

    def perform_create(self, serializer):
        if self.request.user.role not in ['administrator', 'scolar_administrator']:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only administrators can create announcements")
        serializer.save(created_by=self.request.user)


class ClubAnnouncementDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an announcement"""
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'public_id'
    serializer_class = ClubAnnouncementSerializer
    queryset = ClubAnnouncement.objects.all()


# ============================================================================
# Statistics Views
# ============================================================================

class ClubManagerStatsView(generics.GenericAPIView):
    """Get statistics for club manager dashboard"""
    permission_classes = [IsClubManager]

    def get(self, request):
        user = request.user
        clubs = Club.objects.filter(president=user)
        
        stats = {
            'clubs_count': clubs.count(),
            'total_events': ClubEvent.objects.filter(club__in=clubs).count(),
            'upcoming_events': ClubEvent.objects.filter(
                club__in=clubs,
                date__gte=timezone.now().date()
            ).count(),
            'completed_events': ClubEvent.objects.filter(
                club__in=clubs,
                status='completed'
            ).count(),
            'reports_count': ClubReport.objects.filter(club__in=clubs).count(),
            'total_members': sum(club.members_count for club in clubs),
        }
        
        return Response(stats)
