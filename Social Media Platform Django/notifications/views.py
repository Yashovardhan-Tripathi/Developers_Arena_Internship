from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .services import visible_notifications


@login_required
def inbox(request):
    items = visible_notifications(request.user)
    return render(request, 'notifications/inbox.html', {'page_obj': Paginator(items, 25).get_page(request.GET.get('page'))})


@login_required
@require_POST
def mark_read(request, pk=None):
    qs = visible_notifications(request.user)
    if pk:
        obj = get_object_or_404(qs, pk=pk)
        obj.is_read = True
        obj.save(update_fields=['is_read'])
    else:
        qs.update(is_read=True)
    return redirect('notifications')
