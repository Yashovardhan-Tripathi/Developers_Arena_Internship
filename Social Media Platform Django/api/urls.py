from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import CommentDeleteView, FriendRequestViewSet, LoginView, LogoutView, MeView, NotificationViewSet, PersonViewSet, PostViewSet, ReportView, SignupView

router = DefaultRouter()
router.register('users', PersonViewSet, basename='api-users')
router.register('posts', PostViewSet, basename='api-posts')
router.register('friend-requests', FriendRequestViewSet, basename='api-friends')
router.register('notifications', NotificationViewSet, basename='api-notifications')

urlpatterns = [
    path('auth/register/', SignupView.as_view(), name='api-register'),
    path('auth/token/', LoginView.as_view(), name='api-token'),
    path('auth/logout/', LogoutView.as_view(), name='api-logout'),
    path('me/', MeView.as_view(), name='api-me'),
    path('comments/<int:pk>/', CommentDeleteView.as_view(), name='api-comment-delete'),
    path('reports/', ReportView.as_view(), name='api-report'),
    path('', include(router.urls)),
]
