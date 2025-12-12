from django.urls import path

from .views import (
    UserCreateView,
    UserDeleteView,
    UserDetailView,
    UserListView,
    UserUpdateView,
    EducationHistoryCreateView,
    EducationHistoryDeleteView,
    EducationHistoryDetailView,
    EducationHistoryListView,
    EducationHistoryUpdateView,
)

urlpatterns = [
    path("", UserListView.as_view(), name="user-list"),
    path("create/", UserCreateView.as_view(), name="user-create"),
    path("<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("<int:pk>/update/", UserUpdateView.as_view(), name="user-update"),
    path("<int:pk>/delete/", UserDeleteView.as_view(), name="user-delete"),
    path(
        "<int:user_pk>/education-history/",
        EducationHistoryListView.as_view(),
        name="education-history-list",
    ),
    path(
        "<int:user_pk>/education-history/create/",
        EducationHistoryCreateView.as_view(),
        name="education-history-create",
    ),
    path(
        "<int:user_pk>/education-history/<int:pk>/",
        EducationHistoryDetailView.as_view(),
        name="education-history-detail",
    ),
    path(
        "<int:user_pk>/education-history/<int:pk>/update/",
        EducationHistoryUpdateView.as_view(),
        name="education-history-update",
    ),
    path(
        "<int:user_pk>/education-history/<int:pk>/delete/",
        EducationHistoryDeleteView.as_view(),
        name="education-history-delete",
    ),
]
