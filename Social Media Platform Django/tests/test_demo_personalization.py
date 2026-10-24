from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from rest_framework.authtoken.models import Token

from friends.models import Follow, FriendRequest
from notifications.models import Notification
from posts.models import Comment, Like, Post
from users.demo_data import DEMO_PEOPLE, DEMO_STORIES
from users.management.commands.personalize_demo import LEGACY_STORIES, LEGACY_USERNAMES
from users.models import UserProfile


@override_settings(DEBUG=True)
class PersonalizationTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.people = [User.objects.create_user(name, password='ExistingPassword42!') for name in LEGACY_USERNAMES]
        self.admin = User.objects.create_superuser('yashovardhan', 'admin@example.test', 'AdminPassword42!')
        self.admin.profile.bio = 'Existing administrator biography'
        self.admin.profile.save()
        self.posts = [Post.objects.create(author=self.people[index], content=content) for index, content in zip([1, 2, 3, 0], LEGACY_STORIES)]
        self.comment = Comment.objects.create(author=self.admin, post=self.posts[1], content='Keep this administrator comment')
        FriendRequest.objects.create(sender=self.people[0], receiver=self.people[1], status='accepted')
        Follow.objects.create(follower=self.people[1], following=self.people[0])
        Like.objects.create(user=self.people[0], post=self.posts[0])
        Notification.objects.create(actor=self.people[1], recipient=self.people[0], verb='started following you')
        Token.objects.create(user=self.people[0])

    def test_personalization_preserves_identity_credentials_relationships_and_admin(self):
        User = get_user_model()
        admin_before = User.objects.filter(pk=self.admin.pk).values().get()
        profile_before = UserProfile.objects.filter(user=self.admin).values().get()
        hashes = {u.pk: u.password for u in self.people}
        relationships = {model: list(model.objects.values()) for model in [FriendRequest, Follow, Like, Notification, Token]}
        post_ids = [p.pk for p in self.posts]
        call_command('personalize_demo', stdout=StringIO())
        for original, person in zip(self.people, DEMO_PEOPLE):
            original.refresh_from_db()
            username, first, last, email, location, bio = person
            self.assertEqual((original.username, original.first_name, original.last_name, original.email), (username, first, last, email))
            self.assertEqual((original.profile.location, original.profile.bio), (location, bio))
            self.assertEqual(original.password, hashes[original.pk])
        self.assertEqual(User.objects.filter(pk=self.admin.pk).values().get(), admin_before)
        self.assertEqual(UserProfile.objects.filter(user=self.admin).values().get(), profile_before)
        for model, rows in relationships.items():
            self.assertEqual(list(model.objects.values()), rows)
        self.assertEqual(list(Post.objects.filter(pk__in=post_ids).order_by('pk').values_list('pk', flat=True)), post_ids)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Keep this administrator comment')
        counts = (User.objects.count(), Post.objects.count(), Comment.objects.count())
        call_command('personalize_demo', stdout=StringIO())
        self.assertEqual((User.objects.count(), Post.objects.count(), Comment.objects.count()), counts)
        self.assertEqual(Post.objects.get(pk=self.posts[0].pk).content, DEMO_STORIES[0][1])

    def test_target_collision_changes_nothing(self):
        get_user_model().objects.create_user('YASHTRI21')
        before = list(get_user_model().objects.order_by('pk').values())
        with self.assertRaises(CommandError):
            call_command('personalize_demo', stdout=StringIO())
        self.assertEqual(list(get_user_model().objects.order_by('pk').values()), before)

    def test_staff_demo_account_is_protected(self):
        self.people[2].is_staff = True
        self.people[2].save()
        with self.assertRaises(CommandError):
            call_command('personalize_demo', stdout=StringIO())
        self.assertTrue(get_user_model().objects.filter(username=LEGACY_USERNAMES[0]).exists())

    @override_settings(DEBUG=False)
    def test_production_personalization_is_refused(self):
        with self.assertRaises(CommandError):
            call_command('personalize_demo', stdout=StringIO())

    def test_seed_refuses_to_duplicate_original_accounts(self):
        with self.assertRaises(CommandError):
            call_command('seed_demo', password='DemoPassword42!', stdout=StringIO())
        self.assertEqual(get_user_model().objects.count(), 7)


@override_settings(DEBUG=True)
class ApprovedSeedTests(TestCase):
    def test_seed_uses_approved_profiles_and_reruns_without_duplicates_or_password_changes(self):
        call_command('seed_demo', password='DemoPassword42!', stdout=StringIO())
        User = get_user_model()
        self.assertEqual(set(User.objects.values_list('username', flat=True)), {p[0] for p in DEMO_PEOPLE})
        hashes = dict(User.objects.values_list('username', 'password'))
        counts = (User.objects.count(), Post.objects.count(), Comment.objects.count())
        call_command('seed_demo', password='DifferentPassword42!', stdout=StringIO())
        self.assertEqual((User.objects.count(), Post.objects.count(), Comment.objects.count()), counts)
        self.assertEqual(dict(User.objects.values_list('username', 'password')), hashes)
