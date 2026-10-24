def unread_count(request):
    if not request.user.is_authenticated:
        return {'unread_count': 0}
    from .services import visible_notifications
    return {'unread_count': visible_notifications(request.user).filter(is_read=False).count()}
