from rest_framework import serializers
from .models import Club, ClubEvent, ClubReport, ClubAnnouncement
from users.serializers import UserSerializer


class ClubSerializer(serializers.ModelSerializer):
    president_name = serializers.SerializerMethodField()
    events_count = serializers.SerializerMethodField()

    class Meta:
        model = Club
        fields = [
            'id', 'public_id', 'name', 'description', 'logo',
            'president', 'president_name', 'status', 'members_count',
            'events_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'public_id', 'created_at', 'updated_at']

    def get_president_name(self, obj):
        if obj.president:
            return f"{obj.president.first_name} {obj.president.last_name}"
        return None

    def get_events_count(self, obj):
        return obj.events.count()


class ClubCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ['name', 'description', 'logo']


class ClubUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ['name', 'description', 'logo', 'status', 'members_count']


class ClubEventSerializer(serializers.ModelSerializer):
    club_name = serializers.CharField(source='club.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ClubEvent
        fields = [
            'id', 'public_id', 'club', 'club_name', 'title', 'description',
            'date', 'start_time', 'end_time', 'location', 'status',
            'expected_attendees', 'actual_attendees', 'created_by',
            'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'public_id', 'created_by', 'created_at', 'updated_at']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None


class ClubEventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubEvent
        fields = [
            'club', 'title', 'description', 'date', 'start_time',
            'end_time', 'location', 'expected_attendees'
        ]


class ClubReportSerializer(serializers.ModelSerializer):
    club_name = serializers.CharField(source='club.name', read_only=True)
    semester_display = serializers.CharField(source='get_semester_display', read_only=True)

    class Meta:
        model = ClubReport
        fields = [
            'id', 'public_id', 'club', 'club_name', 'semester', 'semester_display',
            'academic_year', 'title', 'content', 'events_organized',
            'total_attendees', 'budget_used', 'achievements', 'challenges',
            'next_semester_plans', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'public_id', 'created_by', 'created_at', 'updated_at']


class ClubReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubReport
        fields = [
            'club', 'semester', 'academic_year', 'title', 'content',
            'events_organized', 'total_attendees', 'budget_used',
            'achievements', 'challenges', 'next_semester_plans'
        ]


class ClubAnnouncementSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = ClubAnnouncement
        fields = [
            'id', 'public_id', 'title', 'content', 'priority', 'priority_display',
            'target_clubs', 'is_global', 'is_active', 'expires_at',
            'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'public_id', 'created_by', 'created_at', 'updated_at']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}"
        return None


class ClubAnnouncementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubAnnouncement
        fields = [
            'title', 'content', 'priority', 'target_clubs', 'is_global', 'expires_at'
        ]
