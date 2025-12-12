from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import models
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User, EducationHistory
from .serializers import (
    ForgotPasswordSerializer,
    LoginSerializer,
    PasswordChangeSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
    EducationHistorySerializer,
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        data = serializer.validated_data
        data["user"] = UserSerializer(user).data
        return Response(data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password updated successfully."})


class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=serializer.validated_data["email"])
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_path = reverse("users:password-reset")
        reset_link = f"{request.build_absolute_uri(reset_path)}?uid={uid}&token={token}&email={user.email}"
        send_mail(
            subject="Password reset request",
            message=f"Reset your password using this link: {reset_link}",
            from_email=None,
            recipient_list=[user.email],
        )
        return Response({"detail": "Password reset email sent."})


class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password has been reset."})


class EducationHistoryCreateView(generics.CreateAPIView):
    """
    POST /api/users/<user_pk>/education-history/
    Create a new education history record for a specific user (Admin only)
    """
    serializer_class = EducationHistorySerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        user = get_object_or_404(User, pk=self.kwargs["user_pk"])
        if user.role != User.Role.STUDENT:
            raise serializers.ValidationError("Only students can have education history.")
        serializer.save(student=user)


class EducationHistoryListView(generics.ListAPIView):
    """
    GET /api/users/<user_pk>/education-history/
    List all education history records for a specific user (Admin only)
    """
    serializer_class = EducationHistorySerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs["user_pk"])
        return user.education_histories.all()


class EducationHistoryDetailView(generics.RetrieveAPIView):
    """
    GET /api/users/<user_pk>/education-history/<pk>/
    Retrieve a specific education history record for a specific user (Admin only)
    """
    serializer_class = EducationHistorySerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs["user_pk"])
        return user.education_histories.all()


class EducationHistoryUpdateView(generics.UpdateAPIView):
    """
    PUT/PATCH /api/users/<user_pk>/education-history/<pk>/update/
    Update a specific education history record for a specific user (Admin only)
    """
    serializer_class = EducationHistorySerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs["user_pk"])
        return user.education_histories.all()

    def perform_update(self, serializer):
        user = get_object_or_404(User, pk=self.kwargs["user_pk"])
        if user.role != User.Role.STUDENT:
            raise serializers.ValidationError("Only students can have education history.")
        serializer.save(student=user)


class EducationHistoryDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/users/<user_pk>/education-history/<pk>/delete/
    Delete a specific education history record for a specific user (Admin only)
    """
    serializer_class = EducationHistorySerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs["user_pk"])
        return user.education_histories.all()

    def perform_destroy(self, instance):
        student_email = instance.student.email
        academic_year = instance.academic_year
        instance.delete()
        return Response(
            {"detail": f"Education history record for '{student_email}' for academic year '{academic_year}' deleted successfully."},
            status=status.HTTP_200_OK
        )


# ============================================================================
# CRUD API Views for User Management
# ============================================================================


class UserListView(generics.ListAPIView):
    """
    GET /api/users/
    List all users (Admin only)
    Supports filtering by role, is_active, and search by email/name
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by role
        role = self.request.query_params.get('role', None)
        if role:
            queryset = queryset.filter(role=role)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Search by email, first_name, or last_name
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                models.Q(email__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search)
            )
        
        return queryset


class UserCreateView(generics.CreateAPIView):
    """
    POST /api/users/create/
    Create a new user (Admin only)
    """
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "detail": "User created successfully.",
                "user": UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )


class UserDetailView(generics.RetrieveAPIView):
    """
    GET /api/users/<id>/
    Retrieve a specific user by ID (Admin only)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class UserUpdateView(generics.UpdateAPIView):
    """
    PUT/PATCH /api/users/<id>/update/
    Update user details (Admin only)
    """
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAdminUser]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "detail": "User updated successfully.",
                "user": UserSerializer(user).data
            }
        )


class UserDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/users/<id>/delete/
    Delete a user (Admin only)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        email = instance.email
        self.perform_destroy(instance)
        return Response(
            {"detail": f"User '{email}' deleted successfully."},
            status=status.HTTP_200_OK
        )


