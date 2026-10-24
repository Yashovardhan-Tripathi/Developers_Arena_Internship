from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'actor', 'verb', 'is_read', 'created_at']
    list_filter = ['is_read']
    readonly_fields = ['recipient', 'actor', 'verb', 'post', 'created_at']
