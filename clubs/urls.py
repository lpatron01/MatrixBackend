from django.urls import path
from . import views

urlpatterns = [
    # Clubs
    path('', views.ClubListCreateView.as_view(), name='club-list-create'),
    path('<uuid:public_id>/', views.ClubDetailView.as_view(), name='club-detail'),
    path('<uuid:public_id>/approve/', views.ClubApproveView.as_view(), name='club-approve'),
    
    # Events
    path('events/', views.ClubEventListCreateView.as_view(), name='event-list-create'),
    path('events/<uuid:public_id>/', views.ClubEventDetailView.as_view(), name='event-detail'),
    
    # Reports
    path('reports/', views.ClubReportListCreateView.as_view(), name='report-list-create'),
    path('reports/<uuid:public_id>/', views.ClubReportDetailView.as_view(), name='report-detail'),
    
    # Announcements
    path('announcements/', views.ClubAnnouncementListCreateView.as_view(), name='announcement-list-create'),
    path('announcements/<uuid:public_id>/', views.ClubAnnouncementDetailView.as_view(), name='announcement-detail'),
    
    # Statistics
    path('stats/', views.ClubManagerStatsView.as_view(), name='club-stats'),
]
