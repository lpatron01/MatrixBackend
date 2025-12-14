from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("users.auth_urls")),
    path("api/users/", include("users.user_urls")),
    path("api/reclamations/", include("reclamations.urls")),
    path("api/documents/", include("document_requests.urls")),
    path("api/classroom/", include("classroom.urls")),
    path("api/schedule/", include("schedule.urls")),
    path("api/chatbot/", include("chatbot.urls")),
    path("api/clubs/", include("clubs.urls")),
]


