from django.conf import settings
from django.db import models
from django.db.models import F, Q


class FriendRequest(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['sender', 'receiver'], name='unique_friend_request'), models.CheckConstraint(condition=~Q(sender=F('receiver')), name='no_self_friend')]


class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following_links')
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='follower_links')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['follower', 'following'], name='unique_follow'), models.CheckConstraint(condition=~Q(follower=F('following')), name='no_self_follow')]


class Block(models.Model):
    blocker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blocking_links')
    blocked = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blocked_by_links')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['blocker', 'blocked'], name='unique_block'), models.CheckConstraint(condition=~Q(blocker=F('blocked')), name='no_self_block')]
