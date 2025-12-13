from rest_framework import serializers
from django.utils import timezone
from .models import Class, Subject, Timetable, Attendance
from users.models import User
from users.serializers import UserSerializer


class SubjectSerializer(serializers.ModelSerializer):
    """Serializer for Subject model"""

    class Meta:
        model = Subject
        fields = ['id', 'name', 'name_arabic', 'code', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ClassSerializer(serializers.ModelSerializer):
    """Serializer for Class model"""
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = ['id', 'name', 'description', 'academic_year', 'is_active', 'student_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_student_count(self, obj):
        return obj.students.count()


class ClassDetailSerializer(ClassSerializer):
    """Detailed serializer for Class with student list"""
    students = UserSerializer(many=True, read_only=True)

    class Meta(ClassSerializer.Meta):
        fields = ClassSerializer.Meta.fields + ['students']


class TimetableSerializer(serializers.ModelSerializer):
    """Serializer for Timetable model"""
    class_room = ClassSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    teacher = UserSerializer(read_only=True)
    time_slot_display = serializers.CharField(source='get_time_slot_display', read_only=True)

    class Meta:
        model = Timetable
        fields = [
            'id', 'class_room', 'subject', 'teacher', 'day_of_week', 'time_slot',
            'time_slot_display', 'classroom', 'academic_year', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TimetableCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating timetable entries"""

    class Meta:
        model = Timetable
        fields = [
            'id', 'class_room', 'subject', 'teacher', 'day_of_week', 'time_slot',
            'classroom', 'academic_year', 'is_active'
        ]
        read_only_fields = ['id']


class AttendanceSerializer(serializers.ModelSerializer):
    """Serializer for Attendance model"""
    student = UserSerializer(read_only=True)
    timetable_entry = TimetableSerializer(read_only=True)
    marked_by = UserSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = [
            'id', 'student', 'timetable_entry', 'date', 'status', 'remarks',
            'marked_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'marked_by']


class AttendanceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating attendance records"""

    class Meta:
        model = Attendance
        fields = ['student', 'timetable_entry', 'date', 'status', 'remarks']

    def create(self, validated_data):
        validated_data['marked_by'] = self.context['request'].user
        return super().create(validated_data)


class AttendanceUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating attendance records"""

    class Meta:
        model = Attendance
        fields = ['status', 'remarks']

    def update(self, instance, validated_data):
        # Update marked_by when attendance is modified
        validated_data['marked_by'] = self.context['request'].user
        return super().update(instance, validated_data)


class StudentAttendanceSerializer(serializers.ModelSerializer):
    """Simplified serializer for student's attendance view"""
    subject = serializers.CharField(source='timetable_entry.subject.name')
    teacher = serializers.CharField(source='timetable_entry.teacher.get_full_name')
    time_slot = serializers.CharField(source='timetable_entry.time_slot')
    classroom = serializers.CharField(source='timetable_entry.classroom')

    class Meta:
        model = Attendance
        fields = ['id', 'date', 'status', 'remarks', 'subject', 'teacher', 'time_slot', 'classroom']


class AttendanceStatsSerializer(serializers.Serializer):
    """Serializer for attendance statistics"""
    total_sessions = serializers.IntegerField()
    present_count = serializers.IntegerField()
    absent_count = serializers.IntegerField()
    late_count = serializers.IntegerField()
    excused_count = serializers.IntegerField()
    attendance_percentage = serializers.FloatField()


class BulkAttendanceSerializer(serializers.Serializer):
    """Serializer for bulk attendance marking"""
    timetable_entry_id = serializers.IntegerField()
    date = serializers.DateField()
    attendances = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        ),
        help_text="List of {student_id: status, remarks: remarks} dicts"
    )

    def validate_date(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError("Cannot mark attendance for future dates")
        return value


class TimetableSessionSerializer(serializers.ModelSerializer):
    """Serializer for session details in attendance marking"""
    class_room = ClassSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    teacher = UserSerializer(read_only=True)
    time_slot_display = serializers.CharField(source='get_time_slot_display', read_only=True)
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Timetable
        fields = [
            'id', 'class_room', 'subject', 'teacher', 'day_of_week', 'time_slot',
            'time_slot_display', 'classroom', 'student_count'
        ]

    def get_student_count(self, obj):
        return obj.class_room.students.count()


class ClassStudentSerializer(serializers.ModelSerializer):
    """Serializer for students in a class (for attendance marking)"""
    full_name = serializers.SerializerMethodField()
    attendance_status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'attendance_status']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_attendance_status(self, obj):
        # This will be populated by the view with current session's attendance
        return getattr(obj, 'current_attendance_status', None)
