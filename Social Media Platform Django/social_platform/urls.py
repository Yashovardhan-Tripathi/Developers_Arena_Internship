from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from friends import views as friend_views
from notifications import views as notification_views
from posts import views as post_views
from users import views as user_views
from users.auth_views import RateLimitedLoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', post_views.health, name='health'),
    path('', post_views.feed, name='feed'),
    path('accounts/signup/', user_views.signup, name='signup'),
    path('accounts/login/', RateLimitedLoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/password/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change.html', success_url='/settings/'), name='password-change'),
    path('settings/', user_views.settings_view, name='settings'),
    path('people/', user_views.people, name='people'),
    path('u/<str:username>/', user_views.profile, name='profile'),
    path('images/profiles/<int:pk>/<str:kind>/', user_views.profile_image, name='profile-image'),
    path('posts/new/', post_views.create_post, name='post-create'),
    path('posts/<int:pk>/', post_views.detail, name='post-detail'),
    path('posts/<int:pk>/edit/', post_views.edit_post, name='post-edit'),
    path('posts/<int:pk>/delete/', post_views.delete_post, name='post-delete'),
    path('posts/<int:pk>/like/', post_views.like, name='post-like'),
    path('posts/<int:pk>/comments/', post_views.comment, name='post-comment'),
    path('comments/<int:pk>/delete/', post_views.delete_comment, name='comment-delete'),
    path('reports/<str:kind>/<int:pk>/', post_views.report, name='report'),
    path('images/posts/<int:pk>/', post_views.post_image, name='post-image'),
    path('connections/', friend_views.connections, name='connections'),
    path('connections/<int:pk>/<str:action>/', friend_views.action, name='connection-action'),
    path('notifications/', notification_views.inbox, name='notifications'),
    path('notifications/read/', notification_views.mark_read, name='notifications-read-all'),
    path('notifications/<int:pk>/read/', notification_views.mark_read, name='notification-read'),
    path('api/', include('api.urls')),
]
admin.site.site_header = 'Gather moderation'
admin.site.site_title = 'Gather admin'
