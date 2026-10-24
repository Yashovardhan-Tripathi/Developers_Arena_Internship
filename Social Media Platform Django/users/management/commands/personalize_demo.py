"""Replace only the original local demo identities, preserving their record IDs."""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from posts.models import Comment, Post
from users.demo_data import DEMO_COMMENTS, DEMO_PEOPLE, DEMO_STORIES


# Historical keys are retained only to locate the original demo records safely.
LEGACY_USERNAMES = ('alex', 'maya', 'james', 'priya', 'david', 'sarah')
LEGACY_STORIES = [
    'A reminder to step away from the screen once in a while. Spent the morning chasing quiet corners and a little green. What’s your favorite way to reset?',
    'Small win today: shipped my first Django side project! Authentication, an API, and a lot of lessons along the way. Grateful for everyone who helped me get unstuck.',
    'Today’s learning: progress doesn’t have to be loud. Sometimes it’s just understanding the error message that confused you yesterday. Keep going.',
    'Happy to be here! Building a little space for real conversations, shared ideas, and everyday moments. What are you working on this week?',
]


class Command(BaseCommand):
    help = 'Personalize the six local demo accounts without changing passwords or the administrator.'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Demo personalization is allowed only with DEBUG=True.')
        User = get_user_model()
        planned = []
        for old, person in zip(LEGACY_USERNAMES, DEMO_PEOPLE):
            target = person[0]
            original = User.objects.filter(username=old).first()
            existing = User.objects.filter(username__iexact=target)
            if original:
                if existing.exclude(pk=original.pk).exists():
                    raise CommandError(f'Target username already belongs to another account: {target}')
                user = original
            else:
                user = User.objects.filter(username=target).first()
                if user is None:
                    raise CommandError(f'Missing demo account for replacement: {old}')
            if user.is_staff or user.is_superuser:
                raise CommandError('Refusing to change a staff or administrator account.')
            planned.append((user, person))

        # A consistent local snapshot is private and ignored by source control.
        database = str(connection.settings_dict['NAME'])
        if connection.vendor == 'sqlite' and Path(database).is_file():
            directory = settings.BASE_DIR / '.local-backups'
            directory.mkdir(exist_ok=True)
            backup = directory / ('before-personalization-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.sqlite3')
            with sqlite3.connect(database) as source, sqlite3.connect(backup) as destination:
                source.backup(destination)
            self.stdout.write(f'Local database backup: {backup}')

        with transaction.atomic():
            untouched = User.objects.exclude(pk__in=[user.pk for user, _ in planned])
            before_users = list(untouched.order_by('pk').values())
            from users.models import UserProfile
            before_profiles = list(UserProfile.objects.filter(user__in=untouched).order_by('pk').values())
            users = {}
            for user, person in planned:
                username, first, last, email, location, bio = person
                user.username, user.first_name, user.last_name, user.email = username, first, last, email
                user.save(update_fields=['username', 'first_name', 'last_name', 'email'])
                profile = user.profile
                profile.bio, profile.location, profile.website = bio, location, ''
                profile.save(update_fields=['bio', 'location', 'website'])
                users[username] = user

            posts = []
            for index, (username, content) in enumerate(DEMO_STORIES):
                author = users[username]
                old_content = LEGACY_STORIES[index] if index < len(LEGACY_STORIES) else content
                matches = Post.objects.filter(author=author, content=old_content)
                if matches.count() > 1:
                    raise CommandError('Ambiguous demo story; no changes committed.')
                post = matches.first()
                if post:
                    post.content = content
                    post.save(update_fields=['content'])
                else:
                    post, _ = Post.objects.get_or_create(author=author, content=content)
                posts.append(post)

            Post.objects.filter(author=users['yashtri21'], content='Local verification: sharing a moment with my circle.').update(
                content='Video ideas for later: Nashik street clips, a quick editing tip, and a behind-the-scenes reel.'
            )
            replacements = [
                (posts[0], users['yashtri21'], 'A long walk with no destination. Works every time.', DEMO_COMMENTS[0][2]),
                (posts[1], users['Prishu28'], 'This is such a good feeling. Congratulations on shipping it!', DEMO_COMMENTS[1][2]),
                (posts[0], users['yashtri21'], 'A little fresh air makes all the difference.', 'The image looks good. Looking forward to your next post.'),
            ]
            for post, author, old, new in replacements:
                Comment.objects.filter(post=post, author=author, content=old).update(content=new)
            for index, username, content in DEMO_COMMENTS:
                Comment.objects.get_or_create(post=posts[index], author=users[username], content=content)

            if before_users != list(untouched.order_by('pk').values()) or before_profiles != list(UserProfile.objects.filter(user__in=untouched).order_by('pk').values()):
                raise CommandError('An unrelated account changed; rolling back all personalization.')

        self.stdout.write(self.style.SUCCESS('Six demo accounts personalized. IDs, passwords and existing relationships preserved; unrelated accounts unchanged.'))
