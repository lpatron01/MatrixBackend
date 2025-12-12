from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import DocumentRequest
from .serializers import (
    DocumentRequestSerializer, 
    DocumentRequestCreateSerializer, 
    DocumentRequestAdminUpdateSerializer,
    DocumentRequestedFileSerializer
)
from users.models import User
from .utlils.demande import generate_document_request_pdf
from django.http import FileResponse, Http404

class DocumentRequestListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['document_type', 'status']
    ordering_fields = ['created_at', 'status']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == User.Role.ADMINISTRATOR:
            return DocumentRequest.objects.all()
        return DocumentRequest.objects.filter(student=user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DocumentRequestCreateSerializer
        return DocumentRequestSerializer

    def perform_create(self, serializer):
        document_request = serializer.save(student=self.request.user)
        # Generate PDF and save its path
        pdf_path = generate_document_request_pdf(document_request)
        document_request.pdf_file = pdf_path
        document_request.save()

class DocumentRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'public_id'
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == User.Role.ADMINISTRATOR:
            return DocumentRequest.objects.all()
        return DocumentRequest.objects.filter(student=user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DocumentRequestAdminUpdateSerializer
        return DocumentRequestSerializer

    def perform_update(self, serializer):
        user = self.request.user
        if not (user.is_staff or user.role == User.Role.ADMINISTRATOR):
             raise permissions.PermissionDenied("You do not have permission to update this request.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if user.is_staff or user.role == User.Role.ADMINISTRATOR:
            instance.delete()
        elif instance.student == user:
            instance.delete()
        else:
            raise permissions.PermissionDenied("You do not have permission to delete this request.")


class TerminateDocumentRequestView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'public_id'
    serializer_class = DocumentRequestAdminUpdateSerializer

    def get_queryset(self):
        return DocumentRequest.objects.all()

    def perform_update(self, serializer):
        user = self.request.user
        if not (user.is_staff or user.role == User.Role.ADMINISTRATOR):
            raise permissions.PermissionDenied("You do not have permission to terminate this request.")
        serializer.instance.status = DocumentRequest.Status.READY
        serializer.save(changed_by=user, comment="Demande terminée.")

class RejectDocumentRequestView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'public_id'
    serializer_class = DocumentRequestAdminUpdateSerializer

    def get_queryset(self):
        return DocumentRequest.objects.all()

    def perform_update(self, serializer):
        user = self.request.user
        if not (user.is_staff or user.role == User.Role.ADMINISTRATOR):
            raise permissions.PermissionDenied("You do not have permission to reject this request.")
        serializer.instance.status = DocumentRequest.Status.REJECTED
        serializer.save(changed_by=user, comment="Demande rejetée.")

class ProcessDocumentRequestView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'public_id'
    serializer_class = DocumentRequestAdminUpdateSerializer

    def get_queryset(self):
        return DocumentRequest.objects.all()

    def perform_update(self, serializer):
        user = self.request.user
        if not (user.is_staff or user.role == User.Role.ADMINISTRATOR):
            raise permissions.PermissionDenied("You do not have permission to process this request.")
        serializer.instance.status = DocumentRequest.Status.IN_PROGRESS
        serializer.save(changed_by=user, comment="Demande en cours de traitement.")


class DocumentRequestFileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'public_id'

    def get_queryset(self):
        return DocumentRequest.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        user = self.request.user

        if not (user.is_staff or user.role == User.Role.ADMINISTRATOR):
            raise permissions.PermissionDenied("You do not have permission to access this file.")

        if not instance.pdf_file:
            raise Http404("PDF file not found for this document request.")
        
        try:
            return FileResponse(instance.pdf_file.open(), content_type='application/pdf')
        except FileNotFoundError:
            raise Http404("PDF file not found on the server.")

class DocumentRequestUploadFileView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'public_id'
    serializer_class = DocumentRequestedFileSerializer

    def get_queryset(self):
        return DocumentRequest.objects.all()

    def perform_update(self, serializer):
        user = self.request.user
        if not (user.is_staff or user.role == User.Role.ADMINISTRATOR):
            raise permissions.PermissionDenied("You do not have permission to upload this file.")
        serializer.save()