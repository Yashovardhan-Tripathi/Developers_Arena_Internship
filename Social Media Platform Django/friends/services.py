from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Q

from .models import Block, Follow, FriendRequest


def blocked_ids(user):
    if not user.is_authenticated:
        return []
    return list(Block.objects.filter(blocker=user).values_list('blocked_id', flat=True)) + list(Block.objects.filter(blocked=user).values_list('blocker_id', flat=True))


def friend_ids(user):
    if not user.is_authenticated:
        return []
    pairs = FriendRequest.objects.filter(Q(sender=user) | Q(receiver=user), status='accepted').values_list('sender_id', 'receiver_id')
    return [b if a == user.pk else a for a, b in pairs]


def people_for(user):
    return get_user_model().objects.filter(is_active=True).exclude(pk__in=blocked_ids(user)).select_related('profile')


def ensure_interaction(actor, target):
    if actor.pk == target.pk:
        raise ValidationError('Choose another person.')
    if not target.is_active or target.pk in blocked_ids(actor):
        raise PermissionDenied('This person is unavailable.')


@transaction.atomic
def request_friend(actor, target):
    # Lock both users in a stable order to serialize requests in either direction.
    list(get_user_model().objects.select_for_update().filter(pk__in=[actor.pk, target.pk]).order_by('pk'))
    ensure_interaction(actor, target)
    if target.pk in friend_ids(actor):
        raise ValidationError('You are already friends.')
    if FriendRequest.objects.filter(sender=target, receiver=actor, status='pending').exists():
        raise ValidationError('This person already sent you a request. Accept it in Connections.')
    obj, created = FriendRequest.objects.get_or_create(sender=actor, receiver=target)
    if not created and obj.status == 'pending':
        return obj
    obj.status = 'pending'
    obj.save(update_fields=['status'])
    from notifications.services import notify
    notify(target, actor, 'sent you a friend request')
    return obj


@transaction.atomic
def respond_request(actor, obj, decision):
    obj = FriendRequest.objects.select_for_update().get(pk=obj.pk)
    if obj.receiver_id != actor.pk:
        raise PermissionDenied('Only the recipient can respond.')
    ensure_interaction(actor, obj.sender)
    if obj.status != 'pending':
        raise ValidationError('This request has already been answered.')
    if decision not in {'accept', 'decline'}:
        raise ValidationError('Choose accept or decline.')
    obj.status = 'accepted' if decision == 'accept' else 'declined'
    obj.save(update_fields=['status'])
    if decision == 'accept':
        from notifications.services import notify
        notify(obj.sender, actor, 'accepted your friend request')
    return obj


def set_follow(actor, target, following):
    ensure_interaction(actor, target)
    if following:
        obj, created = Follow.objects.get_or_create(follower=actor, following=target)
        if created:
            from notifications.services import notify
            notify(target, actor, 'started following you')
    else:
        Follow.objects.filter(follower=actor, following=target).delete()


@transaction.atomic
def set_block(actor, target, blocking):
    if actor.pk == target.pk:
        raise ValidationError('You cannot block yourself.')
    if blocking:
        Block.objects.get_or_create(blocker=actor, blocked=target)
        FriendRequest.objects.filter(Q(sender=actor, receiver=target) | Q(sender=target, receiver=actor)).delete()
        Follow.objects.filter(Q(follower=actor, following=target) | Q(follower=target, following=actor)).delete()
        from notifications.models import Notification
        Notification.objects.filter(Q(actor=actor, recipient=target) | Q(actor=target, recipient=actor)).delete()
    else:
        Block.objects.filter(blocker=actor, blocked=target).delete()
