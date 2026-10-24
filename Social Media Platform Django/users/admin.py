from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'is_private']
    search_fields = ['user__username', 'bio']
