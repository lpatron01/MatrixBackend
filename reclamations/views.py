from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Reclamation
from .serializers import (
    ReclamationSerializer, 
    ReclamationCreateSerializer, 
    ReclamationAdminUpdateSerializer
)
from users.models import User

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_staff or request.user.role == User.Role.ADMINISTRATOR)

class ReclamationListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'is_anonymous']
    ordering_fields = ['created_at', 'status']

    def get_queryset(self):
        user = self.request.user
        # Admins and Scolar Admins see all
        if user.is_staff or user.role in [User.Role.ADMINISTRATOR, User.Role.SCOLAR_ADMINISTRATOR]:
            return Reclamation.objects.all()
        # Teachers see only ENSEIGNEMENT category
        elif user.role == User.Role.TEACHER:
            return Reclamation.objects.filter(category=Reclamation.Category.ENSEIGNEMENT)
        # Students see their own
        return Reclamation.objects.filter(student=user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReclamationCreateSerializer
        return ReclamationSerializer

    def perform_create(self, serializer):
        # Always associate the student so they can track their reclamation
        # Anonymity is handled in the serializer representation
        serializer.save(student=self.request.user)

class ReclamationDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'public_id'
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role in [User.Role.ADMINISTRATOR, User.Role.SCOLAR_ADMINISTRATOR]:
            return Reclamation.objects.all()
        elif user.role == User.Role.TEACHER:
            return Reclamation.objects.filter(category=Reclamation.Category.ENSEIGNEMENT)
        return Reclamation.objects.filter(student=user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            # Only admins should be using this serializer effectively to change status
            return ReclamationAdminUpdateSerializer
        return ReclamationSerializer

    def perform_update(self, serializer):
        # Check permission for update
        user = self.request.user
        if not (user.is_staff or user.role in [User.Role.ADMINISTRATOR, User.Role.SCOLAR_ADMINISTRATOR, User.Role.TEACHER]):
             raise permissions.PermissionDenied("You do not have permission to update this reclamation.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if user.is_staff or user.role in [User.Role.ADMINISTRATOR, User.Role.SCOLAR_ADMINISTRATOR]:
            instance.delete()
        # Student can only delete their own reclamation
        elif instance.student == user:
            instance.delete()
        else:
            raise permissions.PermissionDenied("You do not have permission to delete this reclamation.")
