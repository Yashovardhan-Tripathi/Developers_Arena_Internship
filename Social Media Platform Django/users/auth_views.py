import time

from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.http import HttpResponse


def auth_rate_limited(request):
    # REMOTE_ADDR is deliberately used instead of trusting a user-supplied forwarding header.
    key = f'auth-attempts:{request.META.get("REMOTE_ADDR", "unknown")}:{int(time.time() // 60)}'
    if cache.add(key, 1, timeout=70):
        return False
    try:
        return cache.incr(key) > 15
    except ValueError:
        return False


class RateLimitedLoginView(LoginView):
    template_name = 'registration/login.html'

    def post(self, request, *args, **kwargs):
        if auth_rate_limited(request):
            return HttpResponse('Too many attempts. Try again in one minute.', status=429)
        return super().post(request, *args, **kwargs)
