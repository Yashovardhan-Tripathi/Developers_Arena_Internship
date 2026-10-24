from django.conf import settings
from django.db import models
from .validators import image_path, validate_image


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, max_length=500)
    profile_picture = models.ImageField(upload_to=image_path, blank=True, validators=[validate_image])
    cover_photo = models.ImageField(upload_to=image_path, blank=True, validators=[validate_image])
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    is_private = models.BooleanField(default=False, help_text='Only friends can see your posts, except your Only me posts.')
    default_visibility = models.CharField(max_length=10, choices=[('public', 'Everyone'), ('friends', 'Friends'), ('private', 'Only me')], default='public')
    joined_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} Profile'
