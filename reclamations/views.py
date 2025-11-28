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
        # Admins see all, others see their own
        if user.is_staff or user.role == User.Role.ADMINISTRATOR:
            return Reclamation.objects.all()
        return Reclamation.objects.filter(student=user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReclamationCreateSerializer
        return ReclamationSerializer

    def perform_create(self, serializer):
        is_anonymous = serializer.validated_data.get('is_anonymous', False)
        if is_anonymous:
            serializer.save(student=None)
        else:
            serializer.save(student=self.request.user)

class ReclamationDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'public_id'
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == User.Role.ADMINISTRATOR:
            return Reclamation.objects.all()
        return Reclamation.objects.filter(student=user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            # Only admins should be using this serializer effectively to change status
            return ReclamationAdminUpdateSerializer
        return ReclamationSerializer

    def perform_update(self, serializer):
        # Check permission for update
        user = self.request.user
        if not (user.is_staff or user.role == User.Role.ADMINISTRATOR):
             raise permissions.PermissionDenied("You do not have permission to update this reclamation.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if user.is_staff or user.role == User.Role.ADMINISTRATOR:
            instance.delete()
        # Student can only delete their own reclamation
        elif instance.student == user:
            instance.delete()
        else:
            raise permissions.PermissionDenied("You do not have permission to delete this reclamation.")
