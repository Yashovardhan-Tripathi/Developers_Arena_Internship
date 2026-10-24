import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction

from friends.services import blocked_ids
from .models import Notification

logger = logging.getLogger(__name__)


def notify(recipient, actor, verb, post=None):
    if recipient.pk == actor.pk or recipient.pk in blocked_ids(actor):
        return
    notification = Notification.objects.create(recipient=recipient, actor=actor, verb=verb, post=post)

    def publish():
        try:
            # Re-read eligibility: blocks/privacy can change before commit.
            if not visible_notifications(recipient).filter(pk=notification.pk).exists():
                return
            async_to_sync(get_channel_layer().group_send)(
                f'notifications_{recipient.pk}',
                {'type': 'notification.message', 'id': notification.pk},
            )
        except Exception:
            logger.exception('Notification saved; real-time delivery failed.')
    transaction.on_commit(publish)


def visible_notifications(user):
    from django.db.models import Q
    from posts.services import visible_posts
    return Notification.objects.filter(recipient=user, actor__is_active=True).exclude(
        actor_id__in=blocked_ids(user)
    ).filter(Q(post__isnull=True) | Q(post__in=visible_posts(user))).select_related('actor', 'post')
