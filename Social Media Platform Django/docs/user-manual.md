# Gather user manual

## Start here

Open the local app at http://127.0.0.1:8000. Choose **Create an account**, enter a unique username, email and strong password, then sign up. Sign in using your username, not your email.

If the optional local demo was seeded, use **yashtri21** and the demo password supplied to the seed command. The project contains no built-in production password.

## Profile and privacy

Use **Settings** to edit your name, biography, avatar, cover, location, website, default audience and private-profile setting. Image uploads accept JPEG, PNG or WebP up to 5 MB and 20 megapixels. Use the remove checkbox to clear an existing image.

- **Everyone**: signed-in members may see the post, unless your profile is private or a block applies.
- **Friends**: accepted friends and you may see the post.
- **Only me**: only you may see the post.
- **Private profile**: public/friends posts become visible only to you and accepted friends.

Profile details themselves remain visible to signed-in, non-blocked members. Following a private account does not bypass its audience rules. Changing your default audience affects new posts; editing a post changes that post's audience.

## Posts and conversations

Write in the home composer or use **Create a post**. Choose an audience and optionally attach an image. A post needs text or an image. Posts support up to 5,000 characters.

Use the three-dot menu on your own post to edit or delete it. The delete confirmation is shown in browsers with JavaScript enabled. Likes can be added and removed. **Comment** opens the conversation, where you can write up to 1,000 characters. Comment authors and the post author may delete a comment.

**Share** uses the browser share sheet or copies a link. Sharing never changes who may view a post. Clipboard support may require HTTPS or localhost.

## Find your people

**Discover people** searches names, usernames and biographies. Open a profile to follow, unfollow or send a friend request. **Connections** shows incoming requests, outgoing requests and friends. Accept/decline incoming requests, cancel your own outgoing requests, or remove a friendship.

The home feed has For you, Following and Friends tabs. Search posts from the top bar; use the content filter for photos. “For you” is a chronological feed of visible posts, not an algorithmic recommendation system.

## Notifications

Likes, comments, friend requests, accepted requests and follows create notifications. Self-interactions do not notify you. When the page is open, a WebSocket delivers a toast; **Notifications** holds the saved inbox. Mark individual items or all items read. Offline events remain in the inbox. Reconnect after a network interruption; a toast is not guaranteed for events missed offline.

## Blocking and reporting

Use **Block** on a profile to hide the person in both directions and remove friendship/follows. Settings lists accounts you blocked and allows unblocking. Unblocking does not restore old connections.

Use **Report post** from a post menu or **Report** below a comment, and provide a reason. A report awaits staff review; it does not automatically remove the content.

## Account security

Settings links to **Change your password**. Changing a password invalidates existing mobile API tokens. Website logout ends that browser session. Mobile clients should call /api/auth/logout/ to revoke their token. At present there is no self-service email password reset or email verification; a staff operator handles recovery.

## Staff moderation

Create a superuser with `python manage.py createsuperuser`, then open /admin/. Add staff users with only the required model permissions.

1. Open Reports and filter to Pending.
2. Inspect the target and reason.
3. Select **Hide reported content and resolve reports**, or **Dismiss selected reports**.
4. Review the stored reviewer and timestamp.

Posts and comments can also be hidden/restored through their admin forms. Hidden content is excluded for everyone, including its author. Deactivate abusive accounts through Django's user admin. Moderators should avoid deleting a report's target before reviewing it because target deletion cascades related reports.

## Troubleshooting

- No posts: check the feed tab, search, privacy settings and friendships.
- Upload rejected: check size, dimensions, extension and actual image format.
- No live toast: check WebSocket connectivity and Redis configuration; inspect the saved inbox.
- 403 after a long session: refresh the form to obtain a valid CSRF token.
- Too many attempts: wait one minute before trying the website login again.
