from django.contrib.auth import password_validation
from django.contrib.auth.tokens import default_token_generator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, EducationHistory


class EducationHistorySerializer(serializers.ModelSerializer):
    grade_display = serializers.CharField(source="get_grade_display", read_only=True)
    session_display = serializers.CharField(source="get_session_display", read_only=True)
    result_display = serializers.CharField(source="get_result_display", read_only=True)

    class Meta:
        model = EducationHistory
        fields = (
            "id",
            "academic_year",
            "registration_id",
            "grade",
            "grade_display",
            "specialty",
            "class_name",
            "session",
            "session_display",
            "result",
            "result_display",
        )


class UserSerializer(serializers.ModelSerializer):
    education_histories = EducationHistorySerializer(many=True, read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "role",
            "role_display",
            "cin",
            "date_of_birth",
            "place_of_birth",
            "is_active",
            "is_staff",
            "date_joined",
            "education_histories",
        )
        read_only_fields = ("id", "is_active", "is_staff", "date_joined", "role_display")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("email", "password", "first_name", "last_name", "phone", "role", "cin", "date_of_birth", "place_of_birth")

    def validate_password(self, value):
        password_validation.validate_password(value, self.instance)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for admin to create users"""
    password = serializers.CharField(write_only=True, min_length=8, required=False)

    class Meta:
        model = User
        fields = ("email", "password", "first_name", "last_name", "phone", "role", "cin", "date_of_birth", "place_of_birth", "is_active", "is_staff", "date_joined")

    def validate_cin(self, value):
        """Convert cin from string to int, handle empty values"""
        if value is None or value == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            raise serializers.ValidationError("CIN must be a valid number")

    def validate_password(self, value):
        password_validation.validate_password(value, self.instance)
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        if not password:
            # Generate a random password if not provided
            password = User.objects.make_random_password()
        return User.objects.create_user(password=password, **validated_data)



class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user details"""
    password = serializers.CharField(write_only=True, min_length=8, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("email", "password", "first_name", "last_name", "phone", "role", "cin", "diploma", "date_of_birth", "place_of_birth", "is_active", "is_staff", "date_joined")
        read_only_fields = ("cin",)  # CIN cannot be modified

    def validate_email(self, value):
        """Validate email uniqueness when updating"""
        if value and value != self.instance.email:
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_cin(self, value):
        """Convert cin from string to int, handle empty values"""
        if value is None or value == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            raise serializers.ValidationError("CIN must be a valid number")

    def validate_password(self, value):
        """Validate password if provided"""
        if value:  # Only validate if password is actually provided
            password_validation.validate_password(value, self.instance)
        return value

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:  # Only update password if provided and not empty
            instance.set_password(password)
        instance.save()
        return instance


class LoginSerializer(TokenObtainPairSerializer):
    username_field = User.USERNAME_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["role"] = user.role
        return token


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(_("Incorrect current password."))
        return value

    def validate_new_password(self, value):
        password_validation.validate_password(value, self.context["request"].user)
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError(_("User with this email does not exist."))
        return value


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        token = attrs.get("token")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": _("Invalid user.")})

        if not default_token_generator.check_token(user, token):
            raise serializers.ValidationError({"token": _("Token is invalid or expired.")})

        password_validation.validate_password(attrs["new_password"], user)
        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user


