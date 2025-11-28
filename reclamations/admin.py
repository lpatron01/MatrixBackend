from django.contrib import admin
from .models import Reclamation, ReclamationHistory

class ReclamationHistoryInline(admin.TabularInline):
    model = ReclamationHistory
    extra = 0
    readonly_fields = ('changed_by', 'old_status', 'new_status', 'comment', 'date')

@admin.register(Reclamation)
class ReclamationAdmin(admin.ModelAdmin):
    list_display = ('id', 'public_id', 'category', 'status', 'student', 'is_anonymous', 'created_at')
    list_filter = ('category', 'status', 'is_anonymous')
    search_fields = ('description', 'student__email', 'public_id')
    inlines = [ReclamationHistoryInline]
    readonly_fields = ('public_id', 'created_at', 'updated_at')

@admin.register(ReclamationHistory)
class ReclamationHistoryAdmin(admin.ModelAdmin):
    list_display = ('reclamation', 'changed_by', 'old_status', 'new_status', 'date')
    list_filter = ('date',)
