from django.contrib import admin
from django.contrib.admin.models import LogEntry


class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['action_time', 'user', 'content_type', 'object_repr', 'action_flag']
    list_filter = ['action_time', 'action_flag']
    search_fields = ['object_repr', 'change_message']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'content_type')


# Register the LogEntryAdmin
admin.site.register(LogEntry, LogEntryAdmin)
