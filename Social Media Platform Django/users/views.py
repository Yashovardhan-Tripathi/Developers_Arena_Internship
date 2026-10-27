import mimetypes

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from friends.models import Block, Follow, FriendRequest
from friends.services import friend_ids, people_for
from posts.services import feed_queryset, visible_posts
from .forms import ProfileForm, SignupForm
from rest_framework.decorators import api_view


def signup(request):
    from .auth_views import auth_rate_limited
    from django.http import HttpResponse
    if request.method == 'POST' and auth_rate_limited(request):
        return HttpResponse('Too many attempts. Try again in one minute.', status=429)
    if request.user.is_authenticated:
        return redirect('feed')
    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            user = form.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('feed')
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def profile(request, username):
    person = get_object_or_404(people_for(request.user), username=username)
    posts = feed_queryset(request.user).filter(author=person)
    incoming = FriendRequest.objects.filter(sender=person, receiver=request.user, status='pending').first()
    outgoing = FriendRequest.objects.filter(sender=request.user, receiver=person, status='pending').first()
    return render(request, 'users/profile.html', {
        'person': person, 'page_obj': Paginator(posts, 10).get_page(request.GET.get('page')),
        'is_friend': person.pk in friend_ids(request.user), 'incoming': incoming, 'outgoing': outgoing,
        'is_following': Follow.objects.filter(follower=request.user, following=person).exists(),
        'stats': {'posts': visible_posts(request.user).filter(author=person).count(), 'followers': person.follower_links.count(), 'following': person.following_links.count()},
    })


@login_required
def settings_view(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user.profile)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            form.save()
        messages.success(request, 'Your profile and privacy settings have been saved.')
        return redirect('profile', username=request.user.username)
    blocks = Block.objects.filter(blocker=request.user).select_related('blocked')
    return render(request, 'users/settings.html', {'form': form, 'blocks': blocks})


@login_required
def people(request):
    query = request.GET.get('q', '').strip()[:200]
    users = people_for(request.user).exclude(pk=request.user.pk)
    if query:
        from django.db.models import Q
        users = users.filter(Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(profile__bio__icontains=query))
    return render(request, 'users/people.html', {'query': query, 'page_obj': Paginator(users.order_by('username'), 18).get_page(request.GET.get('page'))})


@api_view(['GET'])
def profile_image(request, pk, kind):
    person = get_object_or_404(people_for(request.user), pk=pk)
    if kind not in {'profile_picture', 'cover_photo'}:
        raise Http404
    image = getattr(person.profile, kind)
    if not image:
        raise Http404
    response = FileResponse(image.open('rb'), content_type=mimetypes.guess_type(image.name)[0] or 'application/octet-stream')
    response['Cache-Control'] = 'private, no-store'
    return response
