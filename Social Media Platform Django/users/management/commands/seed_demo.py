from io import BytesIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from PIL import Image, ImageDraw

from friends.models import Follow, FriendRequest
from notifications.models import Notification
from posts.models import Comment, Like, Post
from users.demo_data import DEMO_COMMENTS, DEMO_PEOPLE, DEMO_STORIES
from .personalize_demo import LEGACY_USERNAMES


class Command(BaseCommand):
    help = 'Create user-approved local demo accounts with drafted sample content. Existing passwords are never changed.'

    def add_arguments(self, parser):
        parser.add_argument('--password', required=True, help='Password for newly created demo accounts')

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Demo data is allowed only with DEBUG=True.')
        if len(options['password']) < 12:
            raise CommandError('Use a demo password of at least 12 characters.')
        if get_user_model().objects.filter(username__in=LEGACY_USERNAMES).exists():
            raise CommandError('Original demo accounts exist. Run personalize_demo before seed_demo to preserve their IDs.')
        users = {}
        for username, first, last, email, location, bio in DEMO_PEOPLE:
            user, created = get_user_model().objects.get_or_create(
                username=username,
                defaults={'first_name': first, 'last_name': last, 'email': email},
            )
            if created:
                user.set_password(options['password'])
                user.save()
                user.profile.bio = bio
                user.profile.location = location
                user.profile.save()
            users[username] = user
        primary, newcomer, gamer, creator, reel_maker, student = [users[p[0]] for p in DEMO_PEOPLE]
        posts = []
        for username, content in DEMO_STORIES:
            obj, _ = Post.objects.get_or_create(author=users[username], content=content)
            posts.append(obj)
        if not posts[0].image:
            image = Image.new('RGB', (1200, 650), '#e2e9ce')
            draw = ImageDraw.Draw(image)
            draw.ellipse((650, -120, 1280, 510), fill='#ced9b1')
            draw.ellipse((815, 50, 1080, 315), fill='#f3edc5')
            draw.polygon([(0, 500), (320, 215), (640, 650), (0, 650)], fill='#6b8d6c')
            draw.polygon([(330, 650), (770, 275), (1200, 650)], fill='#95ab7d')
            draw.polygon([(720, 650), (1130, 400), (1200, 470), (1200, 650)], fill='#537b60')
            draw.rounded_rectangle((52, 48, 325, 102), radius=27, fill='#f7f6e9')
            draw.text((76, 65), 'A LITTLE ROOM TO BREATHE', fill='#456345')
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            posts[0].image.save('demo-landscape.png', ContentFile(buffer.getvalue()))
        for target in [newcomer, gamer]:
            FriendRequest.objects.get_or_create(sender=primary, receiver=target, defaults={'status': 'accepted'})
        FriendRequest.objects.get_or_create(sender=reel_maker, receiver=primary)
        Follow.objects.get_or_create(follower=newcomer, following=primary)
        Follow.objects.get_or_create(follower=gamer, following=primary)
        for actor in [gamer, creator, reel_maker]:
            Like.objects.get_or_create(user=actor, post=posts[0])
        for story_index, username, content in DEMO_COMMENTS:
            Comment.objects.get_or_create(post=posts[story_index], author=users[username], content=content)
        Notification.objects.get_or_create(recipient=primary, actor=reel_maker, verb='sent you a friend request')
        Notification.objects.get_or_create(recipient=primary, actor=newcomer, verb='started following you')
        self.stdout.write(self.style.SUCCESS('Demo data ready. Sign in as yashtri21 with the password you supplied.'))
