from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import FriendRequest
from .services import friend_ids, people_for, request_friend, respond_request, set_block, set_follow


@login_required
def connections(request):
    friends = people_for(request.user).filter(pk__in=friend_ids(request.user)).order_by('username')
    incoming = FriendRequest.objects.filter(receiver=request.user, status='pending', sender__in=people_for(request.user)).select_related('sender__profile')
    outgoing = FriendRequest.objects.filter(sender=request.user, status='pending', receiver__in=people_for(request.user)).select_related('receiver__profile')
    return render(request, 'friends/connections.html', {
        'page_obj': Paginator(friends, 18).get_page(request.GET.get('page')), 'incoming': incoming, 'outgoing': outgoing,
    })


@login_required
@require_POST
def action(request, pk, action):
    target = get_object_or_404(get_user_model(), pk=pk, is_active=True)
    try:
        if action == 'request':
            request_friend(request.user, target)
            messages.success(request, 'Friend request sent.')
        elif action in {'accept', 'decline'}:
            obj = get_object_or_404(FriendRequest, sender=target, receiver=request.user, status='pending')
            respond_request(request.user, obj, action)
            messages.success(request, 'Friend request updated.')
        elif action == 'cancel':
            FriendRequest.objects.filter(sender=request.user, receiver=target, status='pending').delete()
        elif action == 'unfriend':
            FriendRequest.objects.filter(Q(sender=request.user, receiver=target) | Q(sender=target, receiver=request.user), status='accepted').delete()
        elif action in {'follow', 'unfollow'}:
            set_follow(request.user, target, action == 'follow')
        elif action in {'block', 'unblock'}:
            set_block(request.user, target, action == 'block')
            messages.success(request, 'Block settings updated.')
            return redirect('settings')
        else:
            raise ValidationError('Unknown action.')
    except ValidationError as exc:
        messages.error(request, '; '.join(exc.messages))
    return redirect('connections')
