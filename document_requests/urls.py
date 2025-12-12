from django.urls import path
from .views import DocumentRequestListCreateView, DocumentRequestDetailView, TerminateDocumentRequestView, RejectDocumentRequestView, ProcessDocumentRequestView, DocumentRequestFileView, DocumentRequestUploadFileView

app_name = 'document_requests'

urlpatterns = [
    path('demande', DocumentRequestListCreateView.as_view(), name='create-document-request'),
    path('demandes', DocumentRequestListCreateView.as_view(), name='list-document-requests-student'),
    path('demandes/admin', DocumentRequestListCreateView.as_view(), name='list-document-requests-admin'),
    path('demandes/<uuid:public_id>', DocumentRequestDetailView.as_view(), name='document-request-detail'),
    path('demandes/<uuid:public_id>/terminer', TerminateDocumentRequestView.as_view(), name='terminate-document-request'),
    path('demandes/<uuid:public_id>/rejeter', RejectDocumentRequestView.as_view(), name='reject-document-request'),
    path('demandes/<uuid:public_id>/traiter', ProcessDocumentRequestView.as_view(), name='process-document-request'),
    path('demandes/<uuid:public_id>/prefile', DocumentRequestFileView.as_view(), name='document-request-file'),
    path('demandes/<uuid:public_id>/file', DocumentRequestUploadFileView.as_view(), name='document-request-upload-file'),
]
