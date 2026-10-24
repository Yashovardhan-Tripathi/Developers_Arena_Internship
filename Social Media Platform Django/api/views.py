from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied, ValidationError as DjangoValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import generics, permissions, serializers, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, ScopedRateThrottle

from friends.models import Follow, FriendRequest
from friends.services import friend_ids, people_for, request_friend, respond_request, set_block, set_follow
from notifications.services import visible_notifications
from posts.models import Post
from posts.services import add_comment, feed_queryset, report_content, set_like, visible_comments
from .serializers import CommentSerializer, FriendRequestSerializer, NotificationSerializer, PersonSerializer, PostSerializer, ProfileSerializer, ReportSerializer, SignupSerializer


def domain_call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except DjangoValidationError as exc:
        raise serializers.ValidationError(exc.messages)
    except DjangoPermissionDenied as exc:
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied(str(exc))


class LoginView(ObtainAuthToken):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'


class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]

    @transaction.atomic
    def perform_create(self, serializer):
        serializer.save()


class LogoutView(generics.GenericAPIView):
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user.profile


class PersonViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PersonSerializer

    def get_queryset(self):
        qs = people_for(self.request.user).order_by('username')
        query = self.request.query_params.get('q', '').strip()[:200]
        return qs.filter(Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)) if query else qs

    @action(detail=True, methods=['post', 'delete'])
    def follow(self, request, pk=None):
        domain_call(set_follow, request.user, self.get_object(), request.method == 'POST')
        return Response({'following': request.method == 'POST'})

    @action(detail=True, methods=['post'])
    def friend_request(self, request, pk=None):
        obj = domain_call(request_friend, request.user, self.get_object())
        return Response(FriendRequestSerializer(obj, context={'request': request}).data, status=201)

    @action(detail=True, methods=['post', 'delete'])
    def block(self, request, pk=None):
        # Unblocking must still work when the person is excluded from people_for.
        target = get_object_or_404(get_user_model(), pk=pk, is_active=True)
        domain_call(set_block, request.user, target, request.method == 'POST')
        return Response({'blocked': request.method == 'POST'})


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer

    def get_queryset(self):
        qs = feed_queryset(self.request.user)
        query = self.request.query_params.get('q', '').strip()[:200]
        if query:
            qs = qs.filter(content__icontains=query)
        author = self.request.query_params.get('author')
        if author:
            if not author.isdigit():
                raise serializers.ValidationError({'author': 'Use a numeric user ID.'})
            qs = qs.filter(author_id=author)
        tab = self.request.query_params.get('feed')
        if tab == 'following':
            qs = qs.filter(author_id__in=Follow.objects.filter(follower=self.request.user).values('following_id'))
        elif tab == 'friends':
            qs = qs.filter(author_id__in=friend_ids(self.request.user))
        if self.request.query_params.get('kind') == 'photos':
            qs = qs.exclude(image='')
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, visibility=serializer.validated_data.get('visibility', self.request.user.profile.default_visibility))

    def perform_update(self, serializer):
        if serializer.instance.author_id != self.request.user.pk:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only the author can edit this post.')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author_id != self.request.user.pk:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only the author can delete this post.')
        instance.delete()

    @action(detail=True, methods=['post', 'delete'])
    def like(self, request, pk=None):
        post = self.get_object()
        domain_call(set_like, request.user, post, request.method == 'POST')
        return Response({'liked': request.method == 'POST', 'like_count': post.likes.count()})

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        post = self.get_object()
        if request.method == 'POST':
            serializer = CommentSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            obj = domain_call(add_comment, request.user, post, serializer.validated_data['content'])
            return Response(CommentSerializer(obj, context={'request': request}).data, status=201)
        qs = visible_comments(request.user).filter(post=post).select_related('author__profile')
        page = self.paginate_queryset(qs)
        return self.get_paginated_response(CommentSerializer(page, many=True, context={'request': request}).data)


class CommentDeleteView(generics.DestroyAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        return visible_comments(self.request.user)

    def perform_destroy(self, instance):
        if self.request.user.pk not in {instance.author_id, instance.post.author_id}:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only the comment or post author can delete this comment.')
        instance.delete()


class FriendRequestViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        user = self.request.user
        return FriendRequest.objects.filter(Q(sender=user, receiver__in=people_for(user)) | Q(receiver=user, sender__in=people_for(user))).select_related('sender__profile', 'receiver__profile').order_by('-created_at')

    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        obj = domain_call(respond_request, request.user, self.get_object(), request.data.get('decision'))
        return Response(self.get_serializer(obj).data)

    def destroy(self, request, pk=None):
        obj = self.get_object()
        if obj.status == 'pending' and obj.sender_id != request.user.pk:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only the sender can cancel a pending request.')
        obj.delete()
        return Response(status=204)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return visible_notifications(self.request.user)

    @action(detail=True, methods=['post'])
    def read(self, request, pk=None):
        obj = self.get_object()
        obj.is_read = True
        obj.save(update_fields=['is_read'])
        return Response(self.get_serializer(obj).data)

    @action(detail=False, methods=['post'])
    def read_all(self, request):
        self.get_queryset().update(is_read=True)
        return Response({'status': 'read'})


class ReportView(generics.CreateAPIView):
    serializer_class = ReportSerializer

    def perform_create(self, serializer):
        obj = domain_call(report_content, self.request.user, serializer.validated_data['reason'], post=serializer.validated_data.get('post'), comment=serializer.validated_data.get('comment'))
        serializer.instance = obj
