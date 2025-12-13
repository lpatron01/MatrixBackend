from django.contrib import admin
from .models import Class, Subject, Timetable, Attendance


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'academic_year', 'is_active', 'student_count', 'created_at')
    list_filter = ('academic_year', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    filter_horizontal = ('students',)
    readonly_fields = ('created_at', 'updated_at')

    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = 'Number of Students'


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'name_arabic', 'code')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('class_room', 'subject', 'teacher', 'day_of_week', 'time_slot', 'classroom', 'is_active')
    list_filter = ('day_of_week', 'time_slot', 'academic_year', 'is_active', 'class_room', 'subject')
    search_fields = ('class_room__name', 'subject__name', 'teacher__email', 'classroom')
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('class_room', 'subject', 'teacher')


class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    can_delete = True


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('class_room', 'subject', 'teacher', 'day_of_week', 'time_slot', 'classroom', 'is_active')
    list_filter = ('day_of_week', 'time_slot', 'academic_year', 'is_active', 'class_room', 'subject')
    search_fields = ('class_room__name', 'subject__name', 'teacher__email', 'classroom')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [AttendanceInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('class_room', 'subject', 'teacher')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'timetable_entry', 'date', 'status', 'marked_by', 'created_at')
    list_filter = ('status', 'date', 'timetable_entry__subject', 'timetable_entry__class_room')
    search_fields = ('student__email', 'student__first_name', 'student__last_name', 'timetable_entry__subject__name')
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student', 'timetable_entry', 'timetable_entry__subject',
            'timetable_entry__class_room', 'marked_by'
        )

    def timetable_entry(self, obj):
        return f"{obj.timetable_entry.subject.name} - {obj.timetable_entry.day_of_week} {obj.timetable_entry.time_slot}"
    timetable_entry.short_description = 'Session'
