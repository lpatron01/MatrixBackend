from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import StudentGroup, Subject, Session, Attendance, StudentGroupMembership
from users.serializers import UserSerializer

User = get_user_model()


class StudentGroupSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = StudentGroup
        fields = ['id', 'name', 'description', 'level', 'specialty', 'members_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_members_count(self, obj):
        return obj.members.filter(is_active=True).count()


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'description', 'coefficient', 
                  'hours_cours', 'hours_td', 'hours_tp', 'created_at']
        read_only_fields = ['id', 'created_at']


class SessionSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(), 
        source='subject', 
        write_only=True
    )
    teacher = UserSerializer(read_only=True)
    teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='teacher'),
        source='teacher',
        write_only=True,
        required=False,
        allow_null=True
    )
    group = StudentGroupSerializer(read_only=True)
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=StudentGroup.objects.all(),
        source='group',
        write_only=True
    )
    session_type_display = serializers.CharField(source='get_session_type_display', read_only=True)
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = Session
        fields = [
            'id', 'subject', 'subject_id', 'teacher', 'teacher_id',
            'group', 'group_id', 'session_type', 'session_type_display',
            'day_of_week', 'day_of_week_display', 'start_time', 'end_time',
            'room', 'specific_date', 'is_recurring', 'semester', 'academic_year',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SessionListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    group_name = serializers.CharField(source='group.name', read_only=True)
    session_type_display = serializers.CharField(source='get_session_type_display', read_only=True)
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = Session
        fields = [
            'id', 'subject_name', 'subject_code', 'teacher_name', 'group_name',
            'session_type', 'session_type_display', 'day_of_week', 'day_of_week_display',
            'start_time', 'end_time', 'room', 'is_active'
        ]

    def get_teacher_name(self, obj):
        if obj.teacher:
            return f"{obj.teacher.first_name} {obj.teacher.last_name}".strip() or obj.teacher.email
        return None


class AttendanceSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='student'),
        source='student',
        write_only=True
    )
    session = SessionListSerializer(read_only=True)
    session_id = serializers.PrimaryKeyRelatedField(
        queryset=Session.objects.all(),
        source='session',
        write_only=True
    )
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    marked_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = [
            'id', 'session', 'session_id', 'student', 'student_id',
            'date', 'status', 'status_display', 'is_justified', 'justification',
            'justification_file', 'marked_by', 'marked_by_name', 'marked_at', 'updated_at'
        ]
        read_only_fields = ['id', 'marked_by', 'marked_at', 'updated_at']

    def get_marked_by_name(self, obj):
        if obj.marked_by:
            return f"{obj.marked_by.first_name} {obj.marked_by.last_name}".strip() or obj.marked_by.email
        return None


class AttendanceCreateSerializer(serializers.ModelSerializer):
    """For creating/updating attendance records"""
    class Meta:
        model = Attendance
        fields = ['session', 'student', 'date', 'status', 'is_justified', 'justification']

    def create(self, validated_data):
        validated_data['marked_by'] = self.context['request'].user
        return super().create(validated_data)


class BulkAttendanceSerializer(serializers.Serializer):
    """For marking attendance for multiple students at once"""
    session_id = serializers.IntegerField()
    date = serializers.DateField()
    attendances = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )

    def validate_attendances(self, value):
        for item in value:
            if 'student_id' not in item or 'status' not in item:
                raise serializers.ValidationError("Each attendance must have student_id and status")
            if item['status'] not in ['PRESENT', 'ABSENT', 'LATE', 'EXCUSED']:
                raise serializers.ValidationError(f"Invalid status: {item['status']}")
        return value


class StudentGroupMembershipSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='student'),
        source='student',
        write_only=True
    )
    group = StudentGroupSerializer(read_only=True)
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=StudentGroup.objects.all(),
        source='group',
        write_only=True
    )

    class Meta:
        model = StudentGroupMembership
        fields = ['id', 'student', 'student_id', 'group', 'group_id', 'joined_at', 'is_active']
        read_only_fields = ['id', 'joined_at']


class StudentAbsencesSummarySerializer(serializers.Serializer):
    """Summary of student absences"""
    total_sessions = serializers.IntegerField()
    total_absences = serializers.IntegerField()
    justified_absences = serializers.IntegerField()
    unjustified_absences = serializers.IntegerField()
    presence_rate = serializers.FloatField()
    absences = AttendanceSerializer(many=True)
