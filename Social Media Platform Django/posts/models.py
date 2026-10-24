from django.conf import settings
from django.db import models
from users.validators import image_path, validate_image


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(max_length=5000, blank=True)
    image = models.ImageField(upload_to=image_path, blank=True, validators=[validate_image])
    visibility = models.CharField(max_length=10, choices=[('public', 'Everyone'), ('friends', 'Friends'), ('private', 'Only me')], default='public')
    is_hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Like', related_name='liked_posts')

    class Meta:
        ordering = ['-created_at', '-pk']

    def __str__(self):
        return f'Post #{self.pk} by {self.author}'

    def like_count(self):
        return self.likes.count()


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='like_links')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['post', 'user'], name='unique_like')]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(max_length=1000)
    is_hidden = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']


class Report(models.Model):
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    reason = models.TextField(max_length=1000)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('resolved', 'Resolved'), ('dismissed', 'Dismissed')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_reports')
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [models.CheckConstraint(condition=(models.Q(post__isnull=False, comment__isnull=True) | models.Q(post__isnull=True, comment__isnull=False)), name='report_exactly_one_target')]
