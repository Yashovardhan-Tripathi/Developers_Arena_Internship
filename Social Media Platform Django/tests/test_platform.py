from io import BytesIO

from asgiref.sync import async_to_sync
from channels.auth import AuthMiddlewareStack
from channels.routing import URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction
from django.test import Client, TestCase, TransactionTestCase
from django.urls import path
from PIL import Image
from rest_framework.test import APIClient

from friends.models import Block, Follow, FriendRequest
from friends.services import request_friend, respond_request, set_block, set_follow
from notifications.consumers import NotificationConsumer
from notifications.models import Notification
from notifications.services import notify, visible_notifications
from posts.forms import PostForm
from posts.models import Comment, Like, Post, Report
from posts.services import add_comment, visible_posts
from users.validators import validate_image


def image_upload(name='test.png'):
    buf = BytesIO()
    Image.new('RGB', (10, 10), 'green').save(buf, format='PNG')
    return SimpleUploadedFile(name, buf.getvalue(), content_type='image/png')


class PlatformTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.member_one = get_user_model().objects.create_user('member_one', 'member_one@example.test', 'SomeLongPass!42')
        cls.member_two = get_user_model().objects.create_user('member_two', 'member_two@example.test', 'SomeLongPass!42')
        cls.member_three = get_user_model().objects.create_user('member_three', 'member_three@example.test', 'SomeLongPass!42')
        cls.public = Post.objects.create(author=cls.member_two, content='Public hello')
        cls.friends_post = Post.objects.create(author=cls.member_two, content='Friends hello', visibility='friends')
        cls.private = Post.objects.create(author=cls.member_two, content='Secret hello', visibility='private')

    def setUp(self):
        self.client.force_login(self.member_one)
        self.api = APIClient()
        self.api.force_authenticate(self.member_one)

    def test_profile_created_on_registration(self):
        self.assertEqual(self.member_one.profile.user, self.member_one)

    def test_html_signup_and_login(self):
        self.client.logout()
        response = self.client.post('/accounts/signup/', {'username': 'newuser', 'email': 'new@example.test', 'password1': 'UniqueForest42!', 'password2': 'UniqueForest42!'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(get_user_model().objects.filter(username='newuser').exists())
        self.assertEqual(self.client.get('/').status_code, 200)

    def test_api_signup_validates_password(self):
        response = self.api.post('/api/auth/register/', {'username': 'weak', 'email': 'a@example.test', 'password': '123'})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(get_user_model().objects.filter(username='weak').exists())

    def test_token_login_and_revocation(self):
        api = APIClient()
        response = api.post('/api/auth/token/', {'username': 'member_one', 'password': 'SomeLongPass!42'})
        self.assertEqual(response.status_code, 200)
        token = response.data['token']
        api.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        self.assertEqual(api.get('/api/me/').status_code, 200)
        self.assertEqual(api.post('/api/auth/logout/').status_code, 204)
        self.assertEqual(api.get('/api/me/').status_code, 401)

    def test_anonymous_redirect_and_api_denial(self):
        self.client.logout()
        self.assertEqual(self.client.get('/').status_code, 302)
        self.assertEqual(APIClient().get('/api/posts/').status_code, 401)

    def test_csrf_blocks_session_writes(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.member_one)
        self.assertEqual(client.post('/posts/new/', {'content': 'bad', 'visibility': 'public'}).status_code, 403)

    def test_public_friend_private_visibility(self):
        self.assertQuerySetEqual(visible_posts(self.member_one), [self.public], ordered=False)
        obj = request_friend(self.member_one, self.member_two)
        respond_request(self.member_two, obj, 'accept')
        self.assertEqual(set(visible_posts(self.member_one)), {self.public, self.friends_post})
        self.assertEqual(visible_posts(self.member_two).count(), 3)

    def test_private_profile_overrides_public_posts(self):
        self.member_two.profile.is_private = True
        self.member_two.profile.save()
        self.assertFalse(visible_posts(self.member_one).exists())
        self.assertEqual(self.api.get(f'/api/posts/{self.public.pk}/').status_code, 404)

    def test_follow_does_not_grant_private_access(self):
        set_follow(self.member_one, self.member_two, True)
        self.assertFalse(visible_posts(self.member_one).filter(pk=self.friends_post.pk).exists())

    def test_hidden_content_disappears_for_owner_too(self):
        self.public.is_hidden = True
        self.public.save()
        self.assertFalse(visible_posts(self.member_two).filter(pk=self.public.pk).exists())

    def test_block_hides_both_directions_and_removes_connections(self):
        obj = request_friend(self.member_one, self.member_two)
        respond_request(self.member_two, obj, 'accept')
        set_follow(self.member_one, self.member_two, True)
        set_block(self.member_two, self.member_one, True)
        self.assertFalse(visible_posts(self.member_one).exists())
        self.assertFalse(Follow.objects.exists())
        self.assertFalse(FriendRequest.objects.exists())
        self.assertEqual(self.client.get('/u/member_two/').status_code, 404)
        with self.assertRaises(PermissionDenied):
            set_follow(self.member_one, self.member_two, True)

    def test_block_unblock_api(self):
        self.assertEqual(self.api.post(f'/api/users/{self.member_two.pk}/block/').status_code, 200)
        self.assertEqual(self.api.delete(f'/api/users/{self.member_two.pk}/block/').status_code, 200)
        self.assertFalse(Block.objects.exists())

    def test_self_connections_rejected(self):
        for fn in [request_friend, lambda a, b: set_follow(a, b, True), lambda a, b: set_block(a, b, True)]:
            with self.assertRaises(ValidationError):
                fn(self.member_one, self.member_one)

    def test_only_receiver_can_accept(self):
        obj = request_friend(self.member_one, self.member_two)
        with self.assertRaises(PermissionDenied):
            respond_request(self.member_three, obj, 'accept')
        self.assertEqual(self.api.post(f'/api/friend-requests/{obj.pk}/respond/', {'decision': 'accept'}).status_code, 403)

    def test_duplicate_and_reverse_requests(self):
        obj = request_friend(self.member_one, self.member_two)
        self.assertEqual(request_friend(self.member_one, self.member_two).pk, obj.pk)
        with self.assertRaises(ValidationError):
            request_friend(self.member_two, self.member_one)
        self.assertEqual(FriendRequest.objects.count(), 1)

    def test_declined_request_can_be_resent(self):
        obj = request_friend(self.member_one, self.member_two)
        respond_request(self.member_two, obj, 'decline')
        self.assertEqual(request_friend(self.member_one, self.member_two).status, 'pending')

    def test_unfriend_revokes_access(self):
        obj = request_friend(self.member_one, self.member_two)
        respond_request(self.member_two, obj, 'accept')
        self.api.delete(f'/api/friend-requests/{obj.pk}/')
        self.assertFalse(visible_posts(self.member_one).filter(pk=self.friends_post.pk).exists())

    def test_create_update_delete_post(self):
        response = self.api.post('/api/posts/', {'content': 'My own post', 'visibility': 'friends'})
        self.assertEqual(response.status_code, 201)
        pk = response.data['id']
        self.assertEqual(self.api.patch(f'/api/posts/{pk}/', {'content': 'Updated'}).status_code, 200)
        self.assertEqual(self.api.delete(f'/api/posts/{pk}/').status_code, 204)

    def test_empty_post_rejected(self):
        self.assertEqual(self.api.post('/api/posts/', {'content': '  '}).status_code, 400)
        self.assertFalse(PostForm(data={'content': '', 'visibility': 'public'}).is_valid())

    def test_author_cannot_be_spoofed(self):
        response = self.api.post('/api/posts/', {'content': 'Mine', 'author': self.member_two.pk})
        self.assertEqual(Post.objects.get(pk=response.data['id']).author_id, self.member_one.pk)

    def test_cannot_edit_or_delete_another_users_post(self):
        self.assertEqual(self.api.patch(f'/api/posts/{self.public.pk}/', {'content': 'hacked'}).status_code, 403)
        self.assertEqual(self.api.delete(f'/api/posts/{self.public.pk}/').status_code, 403)
        self.assertEqual(self.client.post(f'/posts/{self.public.pk}/delete/').status_code, 404)

    def test_like_idempotent_and_notifies_once(self):
        for _ in range(2):
            self.assertEqual(self.api.post(f'/api/posts/{self.public.pk}/like/').status_code, 200)
        self.assertEqual(Like.objects.count(), 1)
        self.assertEqual(Notification.objects.filter(verb='liked your post').count(), 1)
        self.api.delete(f'/api/posts/{self.public.pk}/like/')
        self.assertEqual(Like.objects.count(), 0)

    def test_cannot_interact_with_private_post(self):
        self.assertEqual(self.api.post(f'/api/posts/{self.private.pk}/like/').status_code, 404)
        self.assertEqual(self.api.post(f'/api/posts/{self.private.pk}/comments/', {'content': 'no'}).status_code, 404)

    def test_comment_creation_and_author_delete(self):
        response = self.api.post(f'/api/posts/{self.public.pk}/comments/', {'content': 'A thoughtful reply'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Notification.objects.filter(verb='commented on your post').count(), 1)
        self.assertEqual(self.api.delete(f"/api/comments/{response.data['id']}/").status_code, 204)

    def test_comment_deletion_permissions(self):
        obj = add_comment(self.member_three, self.public, 'Hello')
        self.assertEqual(self.api.delete(f'/api/comments/{obj.pk}/').status_code, 403)
        self.api.force_authenticate(self.member_two)
        self.assertEqual(self.api.delete(f'/api/comments/{obj.pk}/').status_code, 204)

    def test_hidden_and_blocked_comments_filtered(self):
        Comment.objects.create(post=self.public, author=self.member_three, content='Hidden', is_hidden=True)
        Comment.objects.create(post=self.public, author=self.member_three, content='Blocked')
        set_block(self.member_one, self.member_three, True)
        self.assertEqual(self.api.get(f'/api/posts/{self.public.pk}/comments/').data['count'], 0)

    def test_profile_update_and_email_not_exposed(self):
        self.assertEqual(self.api.patch('/api/me/', {'bio': 'Hello world', 'is_private': True}).status_code, 200)
        response = self.api.get(f'/api/users/{self.member_two.pk}/')
        self.assertNotIn('email', response.data)
        self.assertNotIn('password', response.data)

    def test_default_post_privacy(self):
        self.member_one.profile.default_visibility = 'private'
        self.member_one.profile.save()
        response = self.api.post('/api/posts/', {'content': 'Default private'})
        self.assertEqual(response.data['visibility'], 'private')

    def test_search_and_following_filters(self):
        self.assertEqual(self.api.get('/api/posts/?q=Public').data['count'], 1)
        self.assertEqual(self.api.get('/api/posts/?feed=following').data['count'], 0)
        set_follow(self.member_one, self.member_two, True)
        self.assertEqual(self.api.get('/api/posts/?feed=following').data['count'], 1)
        self.assertEqual(self.api.get('/api/posts/?author=invalid').status_code, 400)

    def test_report_and_moderation(self):
        response = self.api.post('/api/reports/', {'post': self.public.pk, 'reason': 'Abusive content'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Report.objects.get().status, 'pending')
        self.public.is_hidden = True
        self.public.save()
        self.assertEqual(self.api.get(f'/api/posts/{self.public.pk}/').status_code, 404)

    def test_report_requires_exactly_one_visible_target(self):
        self.assertEqual(self.api.post('/api/reports/', {'reason': 'No target'}).status_code, 400)
        self.assertEqual(self.api.post('/api/reports/', {'post': self.private.pk, 'reason': 'Unavailable'}).status_code, 403)

    def test_notification_ownership_and_read(self):
        notify(self.member_two, self.member_three, 'started following you')
        obj = Notification.objects.get()
        self.assertEqual(self.api.get('/api/notifications/').data['count'], 0)
        self.assertEqual(self.api.post(f'/api/notifications/{obj.pk}/read/').status_code, 404)
        self.api.force_authenticate(self.member_two)
        self.assertEqual(self.api.post(f'/api/notifications/{obj.pk}/read/').status_code, 200)
        obj.refresh_from_db()
        self.assertTrue(obj.is_read)

    def test_self_notification_suppressed(self):
        notify(self.member_one, self.member_one, 'liked your post', self.public)
        self.assertEqual(Notification.objects.count(), 0)

    def test_notification_privacy_rechecked(self):
        notify(self.member_one, self.member_two, 'liked your post', self.public)
        self.public.visibility = 'private'
        self.public.save()
        self.assertFalse(visible_notifications(self.member_one).exists())

    def test_image_upload_and_protected_access(self):
        response = self.api.post('/api/posts/', {'content': 'Picture', 'visibility': 'private', 'image': image_upload()}, format='multipart')
        self.assertEqual(response.status_code, 201)
        pk = response.data['id']
        self.assertEqual(self.client.get(f'/images/posts/{pk}/').status_code, 200)
        self.client.force_login(self.member_two)
        self.assertEqual(self.client.get(f'/images/posts/{pk}/').status_code, 404)
        self.assertEqual(self.client.get('/media/images/test.png').status_code, 404)

    def test_reject_disguised_and_oversized_uploads(self):
        fake = SimpleUploadedFile('bad.png', b'<script>alert(1)</script>', content_type='image/png')
        self.assertEqual(self.api.post('/api/posts/', {'image': fake}, format='multipart').status_code, 400)
        with self.assertRaises(ValidationError):
            validate_image(SimpleUploadedFile('huge.png', b'x' * (5 * 1024 * 1024 + 1)))

    def test_html_escapes_user_content(self):
        obj = Post.objects.create(author=self.member_two, content='<script>alert("xss")</script>')
        response = self.client.get(f'/posts/{obj.pk}/')
        self.assertNotContains(response, '<script>alert')
        self.assertContains(response, '&lt;script&gt;')

    def test_all_main_pages_render(self):
        for url in ['/', '/?tab=friends', '/?tab=following', '/people/', '/connections/', '/notifications/', '/settings/', '/u/member_two/', '/posts/new/', f'/posts/{self.public.pk}/', '/accounts/password/']:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_database_like_uniqueness(self):
        Like.objects.create(user=self.member_one, post=self.public)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Like.objects.create(user=self.member_one, post=self.public)

    def test_post_mutations_require_post_method(self):
        self.assertEqual(self.client.get(f'/posts/{self.public.pk}/like/').status_code, 405)

    def test_health_check(self):
        self.assertEqual(self.client.get('/health/').json(), {'status': 'ok'})

    def test_token_can_fetch_protected_image(self):
        response = self.api.post('/api/posts/', {'image': image_upload(), 'visibility': 'private'}, format='multipart')
        from rest_framework.authtoken.models import Token
        token = Token.objects.create(user=self.member_one)
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertEqual(client.get(response.data['image_url']).status_code, 200)

    def test_image_filename_must_be_safe(self):
        with self.assertRaises(ValidationError):
            validate_image(image_upload('picture.html'))
        with self.assertRaises(ValidationError):
            validate_image(image_upload('picture.jpg'))

    def test_password_change_revokes_mobile_token(self):
        from rest_framework.authtoken.models import Token
        Token.objects.create(user=self.member_one)
        self.member_one.set_password('ChangedPassword42!')
        self.member_one.save()
        self.assertFalse(Token.objects.filter(user=self.member_one).exists())

    def test_private_image_widgets_render_and_do_not_expose_storage(self):
        self.member_one.profile.profile_picture.save('test.png', image_upload())
        response = self.client.get('/settings/')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '/media/')
        self.assertContains(response, 'An image is currently uploaded.')

    def test_profile_image_api_upload(self):
        response = self.api.patch('/api/me/', {'profile_picture': image_upload()}, format='multipart')
        self.assertEqual(response.status_code, 200)
        self.assertIn('/images/profiles/', response.data['profile_picture'])
        self.assertEqual(self.api.get(response.data['profile_picture']).status_code, 200)

    def test_post_edit_can_clear_image(self):
        post = Post.objects.create(author=self.member_one, content='With image', image=image_upload())
        self.assertEqual(self.client.get(f'/posts/{post.pk}/edit/').status_code, 200)
        response = self.client.post(f'/posts/{post.pk}/edit/', {'content': 'No image now', 'visibility': 'public', 'image-clear': 'on'})
        self.assertEqual(response.status_code, 302)
        post.refresh_from_db()
        self.assertFalse(post.image)


class WebsocketTests(TransactionTestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('socketuser', password='SomeLongPass!42')

    def application(self):
        return AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter([
            path('ws/notifications/', NotificationConsumer.as_asgi()),
        ])))

    def test_anonymous_socket_rejected(self):
        async def run():
            socket = WebsocketCommunicator(self.application(), '/ws/notifications/', headers=[(b'origin', b'http://testserver')])
            connected, _ = await socket.connect()
            self.assertFalse(connected)
            await socket.disconnect()
        async_to_sync(run)()

    def test_foreign_origin_rejected(self):
        async def run():
            socket = WebsocketCommunicator(self.application(), '/ws/notifications/', headers=[(b'origin', b'https://evil.example')])
            connected, _ = await socket.connect()
            self.assertFalse(connected)
            await socket.disconnect()
        async_to_sync(run)()

    def test_authenticated_socket_delivers_saved_notification(self):
        actor = get_user_model().objects.create_user('actor', password='SomeLongPass!42')
        client = Client()
        client.force_login(self.user)
        cookie = client.cookies['sessionid'].value
        async def run():
            from channels.db import database_sync_to_async
            socket = WebsocketCommunicator(self.application(), '/ws/notifications/', headers=[
                (b'origin', b'http://testserver'), (b'cookie', f'sessionid={cookie}'.encode()),
            ])
            connected, _ = await socket.connect()
            self.assertTrue(connected)
            self.assertEqual((await socket.receive_json_from())['type'], 'connected')
            await database_sync_to_async(notify)(self.user, actor, 'started following you')
            payload = await socket.receive_json_from()
            self.assertEqual(payload['type'], 'notification')
            self.assertIn('actor', payload['message'])
            await socket.disconnect()
        async_to_sync(run)()
