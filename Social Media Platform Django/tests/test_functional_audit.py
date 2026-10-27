"""Additional user workflows and boundary checks from the functionality audit."""
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import RequestFactory, TestCase
from rest_framework.test import APIClient

from friends.models import Block, Follow, FriendRequest
from posts.models import Comment, Post, Report


class FunctionalAuditTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = get_user_model().objects.create_user('audit_owner', password='ForestTrail42!')
        cls.peer = get_user_model().objects.create_user('audit_peer', password='ForestTrail42!')
        cls.post = Post.objects.create(author=cls.peer, content='Audit story')

    def setUp(self):
        cache.clear()
        self.client.force_login(self.owner)
        self.api = APIClient()
        self.api.force_authenticate(self.owner)

    def test_author_filter_rejects_invalid_numeric_inputs(self):
        for value in ['abc', '\u00b2', '9' * 5000, str(2**63), '-1', '1.2']:
            with self.subTest(value=value[:20]):
                self.assertEqual(self.api.get('/api/posts/', {'author': value}).status_code, 400)
        self.assertEqual(self.api.get('/api/posts/', {'author': str(self.peer.pk)}).data['count'], 1)

    def test_html_post_lifecycle_and_comment(self):
        response = self.client.post('/posts/new/', {'content': 'Audit private story', 'visibility': 'private'})
        post = Post.objects.get(author=self.owner, content='Audit private story')
        self.assertRedirects(response, f'/posts/{post.pk}/')
        self.assertEqual(self.client.post(f'/posts/{post.pk}/edit/', {'content': 'Updated story', 'visibility': 'public'}).status_code, 302)
        post.refresh_from_db()
        self.assertEqual((post.content, post.visibility), ('Updated story', 'public'))
        self.client.post(f'/posts/{post.pk}/comments/', {'content': 'A comment'})
        comment = Comment.objects.get(post=post)
        self.client.post(f'/comments/{comment.pk}/delete/')
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())
        self.client.post(f'/posts/{post.pk}/delete/')
        self.assertFalse(Post.objects.filter(pk=post.pk).exists())

    def test_html_social_connection_lifecycle(self):
        url = f'/connections/{self.peer.pk}/'
        self.client.post(url + 'request/')
        request = FriendRequest.objects.get(sender=self.owner, receiver=self.peer)
        self.client.force_login(self.peer)
        self.client.post(f'/connections/{self.owner.pk}/accept/')
        request.refresh_from_db()
        self.assertEqual(request.status, 'accepted')
        self.client.force_login(self.owner)
        self.client.post(url + 'follow/')
        self.assertTrue(Follow.objects.filter(follower=self.owner, following=self.peer).exists())
        self.client.post(url + 'block/')
        self.assertTrue(Block.objects.filter(blocker=self.owner, blocked=self.peer).exists())
        self.assertFalse(FriendRequest.objects.exists())
        self.assertFalse(Follow.objects.exists())
        self.assertEqual(self.client.get(f'/u/{self.peer.username}/').status_code, 404)
        self.client.post(url + 'unblock/')
        self.assertEqual(self.client.get(f'/u/{self.peer.username}/').status_code, 200)

    def test_html_password_change_preserves_session_and_revokes_token(self):
        from rest_framework.authtoken.models import Token
        Token.objects.create(user=self.owner)
        response = self.client.post('/accounts/password/', {'old_password': 'ForestTrail42!', 'new_password1': 'RiverStone85!', 'new_password2': 'RiverStone85!'})
        self.assertRedirects(response, '/settings/')
        self.owner.refresh_from_db()
        self.assertTrue(self.owner.check_password('RiverStone85!'))
        self.assertFalse(Token.objects.filter(user=self.owner).exists())
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertRedirects(self.client.post('/accounts/logout/'), '/accounts/login/')
        self.assertEqual(self.client.get('/').status_code, 302)

    def test_login_rate_limit(self):
        self.client.logout()
        with patch('users.auth_views.time.time', return_value=6000):
            for _ in range(15):
                self.assertEqual(self.client.post('/accounts/login/', {'username': 'missing', 'password': 'bad'}).status_code, 200)
            self.assertEqual(self.client.post('/accounts/login/', {'username': 'missing', 'password': 'bad'}).status_code, 429)

    def test_moderator_resolves_and_dismisses_reports(self):
        staff = get_user_model().objects.create_superuser('audit_staff', password='ForestTrail42!')
        report = Report.objects.create(reporter=self.owner, post=self.post, reason='Review this')
        request = RequestFactory().post('/admin/posts/report/')
        request.user = staff
        model_admin = admin.site._registry[Report]
        model_admin.hide_content(request, Report.objects.filter(pk=report.pk))
        self.post.refresh_from_db()
        report.refresh_from_db()
        self.assertTrue(self.post.is_hidden)
        self.assertEqual((report.status, report.reviewed_by), ('resolved', staff))
        self.assertIsNotNone(report.reviewed_at)
        self.assertEqual(self.api.get(f'/api/posts/{self.post.pk}/').status_code, 404)
        other = Report.objects.create(reporter=self.owner, comment=Comment.objects.create(author=self.peer, post=self.post, content='Comment'), reason='Review comment')
        model_admin.dismiss_reports(request, Report.objects.filter(pk=other.pk))
        other.refresh_from_db()
        self.assertEqual(other.status, 'dismissed')

    def test_health_returns_service_unavailable_on_database_failure(self):
        with patch('django.db.backends.utils.CursorWrapper.execute', side_effect=RuntimeError('offline')):
            response = self.client.get('/health/')
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {'status': 'unavailable'})
