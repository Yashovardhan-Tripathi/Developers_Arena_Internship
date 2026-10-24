from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import UserProfile


@receiver(post_save, sender=get_user_model())
def ensure_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(pre_save, sender=get_user_model())
def revoke_tokens_on_password_change(sender, instance, **kwargs):
    if instance.pk:
        previous = sender.objects.filter(pk=instance.pk).values_list('password', flat=True).first()
        if previous is not None and previous != instance.password:
            from rest_framework.authtoken.models import Token
            Token.objects.filter(user_id=instance.pk).delete()
