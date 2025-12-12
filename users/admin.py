from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, EducationHistory


class EducationHistoryInline(admin.TabularInline):
    model = EducationHistory
    extra = 0
    can_delete = True


@admin.register(EducationHistory)
class EducationHistoryAdmin(admin.ModelAdmin):
    list_display = ("student", "class_name", "academic_year", "result")
    list_filter = ("academic_year", "grade", "result", "session")
    search_fields = ("student__email", "student__first_name", "student__last_name", "registration_id")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "role", "is_active", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    list_filter = ("role", "is_active", "is_staff")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "role", "cin", "diploma", "date_of_birth", "place_of_birth")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    inlines = [EducationHistoryInline]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "role",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
    filter_horizontal = ("groups", "user_permissions")

