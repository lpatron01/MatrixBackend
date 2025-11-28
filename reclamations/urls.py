from django.urls import path
from .views import ReclamationListCreateView, ReclamationDetailView

app_name = 'reclamations'

urlpatterns = [
    path('', ReclamationListCreateView.as_view(), name='reclamation-list-create'),
    path('<uuid:public_id>/', ReclamationDetailView.as_view(), name='reclamation-detail'),
]
