from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'read', 'timestamp']
    search_fields = ['user__username', 'message']
    list_filter = ['read', 'timestamp']