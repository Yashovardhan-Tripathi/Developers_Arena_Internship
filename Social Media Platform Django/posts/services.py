from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Count, Exists, OuterRef, Prefetch, Q

from friends.services import blocked_ids, friend_ids
from .models import Comment, Like, Post, Report


def visible_posts(user):
    if not user.is_authenticated:
        return Post.objects.none()
    friends = friend_ids(user)
    own = Q(author=user)
    audience = Q(visibility='public', author__profile__is_private=False) | Q(visibility__in=['public', 'friends'], author_id__in=friends)
    # Moderated posts disappear even for their authors.
    return Post.objects.filter(is_hidden=False, author__is_active=True).filter(own | audience).exclude(author_id__in=blocked_ids(user))


def visible_comments(user):
    return Comment.objects.filter(is_hidden=False, author__is_active=True, post__in=visible_posts(user)).exclude(author_id__in=blocked_ids(user))


def feed_queryset(user):
    comments = visible_comments(user).select_related('author__profile')
    return visible_posts(user).select_related('author__profile').annotate(
        total_likes=Count('like_links', distinct=True),
        liked_by_me=Exists(Like.objects.filter(post=OuterRef('pk'), user=user)),
    ).prefetch_related(Prefetch('comments', queryset=comments, to_attr='display_comments')).order_by('-created_at', '-pk')


def ensure_post_access(user, post):
    if not visible_posts(user).filter(pk=post.pk).exists():
        raise PermissionDenied('This post is unavailable.')


def set_like(user, post, liked):
    ensure_post_access(user, post)
    if liked:
        _, created = Like.objects.get_or_create(user=user, post=post)
        if created:
            from notifications.services import notify
            notify(post.author, user, 'liked your post', post)
    else:
        Like.objects.filter(user=user, post=post).delete()


def add_comment(user, post, content):
    ensure_post_access(user, post)
    content = content.strip()
    if not content or len(content) > 1000:
        raise ValidationError('Comments must contain 1-1000 characters.')
    comment = Comment.objects.create(author=user, post=post, content=content)
    from notifications.services import notify
    notify(post.author, user, 'commented on your post', post)
    return comment


def report_content(user, reason, post=None, comment=None):
    reason = reason.strip()
    if not reason or len(reason) > 1000:
        raise ValidationError('Enter a reason of 1-1000 characters.')
    if comment:
        if not visible_comments(user).filter(pk=comment.pk).exists():
            raise PermissionDenied('This comment is unavailable.')
    elif post:
        ensure_post_access(user, post)
    else:
        raise ValidationError('Choose content to report.')
    return Report.objects.create(reporter=user, reason=reason, post=post, comment=comment)
