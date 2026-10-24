from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.urls import reverse
from rest_framework import serializers

from friends.models import FriendRequest
from notifications.models import Notification
from posts.models import Comment, Post, Report
from users.models import UserProfile


class PersonSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(source='profile.bio', read_only=True)
    location = serializers.CharField(source='profile.location', read_only=True)
    website = serializers.URLField(source='profile.website', read_only=True)
    is_private = serializers.BooleanField(source='profile.is_private', read_only=True)
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'first_name', 'last_name', 'bio', 'location', 'website', 'is_private', 'profile_picture']

    def get_profile_picture(self, obj):
        if obj.profile.profile_picture:
            return self.context['request'].build_absolute_uri(reverse('profile-image', args=[obj.pk, 'profile_picture']))
        return None


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    email = serializers.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def validate(self, data):
        user = get_user_model()(**{k: v for k, v in data.items() if k != 'password'})
        try:
            validate_password(data['password'], user=user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'password': exc.messages})
        return data

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['bio', 'location', 'website', 'profile_picture', 'cover_photo', 'is_private', 'default_visibility']

    def to_representation(self, obj):
        data = super().to_representation(obj)
        for kind in ['profile_picture', 'cover_photo']:
            data[kind] = self.context['request'].build_absolute_uri(reverse('profile-image', args=[obj.user_id, kind])) if getattr(obj, kind) else None
        return data


class PostSerializer(serializers.ModelSerializer):
    author = PersonSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()
    image = serializers.ImageField(write_only=True, required=False, allow_null=True)
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    liked_by_me = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'image', 'image_url', 'visibility', 'created_at', 'updated_at', 'like_count', 'comment_count', 'liked_by_me']
        read_only_fields = ['created_at', 'updated_at']

    def validate_image(self, value):
        if value:
            from users.validators import validate_image
            validate_image(value)
        return value

    def validate(self, data):
        content = data.get('content', self.instance.content if self.instance else '')
        image = data.get('image', self.instance.image if self.instance else None)
        if not content.strip() and not image:
            raise serializers.ValidationError('Write something or attach an image.')
        return data

    def get_image_url(self, obj):
        return self.context['request'].build_absolute_uri(reverse('post-image', args=[obj.pk])) if obj.image else None

    def get_like_count(self, obj):
        return obj.total_likes if hasattr(obj, 'total_likes') else obj.likes.count()

    def get_comment_count(self, obj):
        if hasattr(obj, 'display_comments'):
            return len(obj.display_comments)
        from posts.services import visible_comments
        return visible_comments(self.context['request'].user).filter(post=obj).count()

    def get_liked_by_me(self, obj):
        return obj.liked_by_me if hasattr(obj, 'liked_by_me') else obj.likes.filter(pk=self.context['request'].user.pk).exists()


class CommentSerializer(serializers.ModelSerializer):
    author = PersonSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at']
        read_only_fields = ['post', 'created_at']


class FriendRequestSerializer(serializers.ModelSerializer):
    sender = PersonSerializer(read_only=True)
    receiver = PersonSerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'status', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    actor = serializers.CharField(source='actor.username')

    class Meta:
        model = Notification
        fields = ['id', 'actor', 'verb', 'post', 'is_read', 'created_at']


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'post', 'comment', 'reason', 'status']
        read_only_fields = ['id', 'status']

    def validate(self, data):
        if bool(data.get('post')) == bool(data.get('comment')):
            raise serializers.ValidationError('Choose exactly one post or comment.')
        return data
