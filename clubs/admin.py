from django.contrib import admin
from .models import Club, ClubEvent, ClubReport, ClubAnnouncement


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['name', 'president', 'status', 'members_count', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description', 'president__email']
    readonly_fields = ['public_id', 'created_at', 'updated_at']


@admin.register(ClubEvent)
class ClubEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'club', 'date', 'status', 'location']
    list_filter = ['status', 'date', 'club']
    search_fields = ['title', 'description', 'club__name']
    readonly_fields = ['public_id', 'created_at', 'updated_at']


@admin.register(ClubReport)
class ClubReportAdmin(admin.ModelAdmin):
    list_display = ['club', 'semester', 'academic_year', 'events_organized', 'created_at']
    list_filter = ['semester', 'academic_year', 'club']
    search_fields = ['title', 'club__name']
    readonly_fields = ['public_id', 'created_at', 'updated_at']


@admin.register(ClubAnnouncement)
class ClubAnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'is_global', 'is_active', 'created_at']
    list_filter = ['priority', 'is_global', 'is_active']
    search_fields = ['title', 'content']
    readonly_fields = ['public_id', 'created_at', 'updated_at']
