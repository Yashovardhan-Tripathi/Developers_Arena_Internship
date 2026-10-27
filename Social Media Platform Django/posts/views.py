import mimetypes

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from friends.models import Follow
from friends.services import friend_ids, people_for
from .forms import PostForm
from rest_framework.decorators import api_view
from .models import Post
from .services import add_comment, feed_queryset, report_content, set_like, visible_comments, visible_posts


@login_required
def feed(request):
    posts = feed_queryset(request.user)
    tab = request.GET.get('tab', 'all')
    if tab == 'following':
        posts = posts.filter(author_id__in=Follow.objects.filter(follower=request.user).values('following_id'))
    elif tab == 'friends':
        posts = posts.filter(author_id__in=friend_ids(request.user))
    else:
        tab = 'all'
    query = request.GET.get('q', '').strip()[:200]
    if query:
        posts = posts.filter(Q(content__icontains=query) | Q(author__username__icontains=query))
    kind = request.GET.get('kind', '')
    if kind == 'photos':
        posts = posts.exclude(image='')
    form = PostForm(initial={'visibility': request.user.profile.default_visibility})
    suggestions = people_for(request.user).exclude(pk=request.user.pk).exclude(
        pk__in=Follow.objects.filter(follower=request.user).values('following_id')
    ).order_by('username')[:4]
    return render(request, 'posts/feed.html', {
        'page_obj': Paginator(posts, 10).get_page(request.GET.get('page')), 'form': form,
        'tab': tab, 'query': query, 'kind': kind, 'suggestions': suggestions,
        'own_posts': Post.objects.filter(author=request.user, is_hidden=False).count(),
        'followers': request.user.follower_links.count(), 'following': request.user.following_links.count(),
    })


@login_required
def create_post(request):
    form = PostForm(request.POST or None, request.FILES or None, initial={'visibility': request.user.profile.default_visibility})
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        messages.success(request, 'Your post is live.')
        return redirect('post-detail', pk=post.pk)
    return render(request, 'posts/form.html', {'form': form, 'heading': 'Create a post'})


@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user, is_hidden=False)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Post updated.')
        return redirect('post-detail', pk=post.pk)
    return render(request, 'posts/form.html', {'form': form, 'heading': 'Edit your post'})


@login_required
def detail(request, pk):
    post = get_object_or_404(feed_queryset(request.user), pk=pk)
    return render(request, 'posts/detail.html', {'post': post, 'show_comments': True})


@login_required
@require_POST
def delete_post(request, pk):
    get_object_or_404(Post, pk=pk, author=request.user).delete()
    messages.success(request, 'Post deleted.')
    return redirect('feed')


@login_required
@require_POST
def like(request, pk):
    post = get_object_or_404(visible_posts(request.user), pk=pk)
    set_like(request.user, post, request.POST.get('liked') == 'true')
    return redirect('post-detail', pk=pk)


@login_required
@require_POST
def comment(request, pk):
    post = get_object_or_404(visible_posts(request.user), pk=pk)
    try:
        add_comment(request.user, post, request.POST.get('content', ''))
    except ValidationError as exc:
        messages.error(request, '; '.join(exc.messages))
    return redirect('post-detail', pk=pk)


@login_required
@require_POST
def delete_comment(request, pk):
    obj = get_object_or_404(visible_comments(request.user), pk=pk)
    if request.user.pk not in {obj.author_id, obj.post.author_id}:
        raise PermissionDenied
    post_id = obj.post_id
    obj.delete()
    return redirect('post-detail', pk=post_id)


@login_required
def report(request, kind, pk):
    target = get_object_or_404(visible_posts(request.user) if kind == 'post' else visible_comments(request.user), pk=pk)
    if kind not in {'post', 'comment'}:
        raise Http404
    if request.method == 'POST':
        try:
            report_content(request.user, request.POST.get('reason', ''), **{kind: target})
        except ValidationError as exc:
            messages.error(request, '; '.join(exc.messages))
        else:
            messages.success(request, 'Report submitted. A moderator will review it.')
            return redirect('feed')
    return render(request, 'posts/report.html', {'target': target})


@api_view(['GET'])
def post_image(request, pk):
    post = get_object_or_404(visible_posts(request.user), pk=pk)
    if not post.image:
        raise Http404
    response = FileResponse(post.image.open('rb'), content_type=mimetypes.guess_type(post.image.name)[0] or 'application/octet-stream')
    response['Cache-Control'] = 'private, no-store'
    return response


def health(request):
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        from django.conf import settings
        if settings.REDIS_URL:
            from django.core.cache import cache
            cache.get('healthcheck')
    except Exception:
        return JsonResponse({'status': 'unavailable'}, status=503)
    return JsonResponse({'status': 'ok'})
