# REST API

Base URL: /api/. Responses are JSON. List responses contain count, next, previous and results, with 20 results per page. All routes require authentication except registration and token issuance. Errors use normal DRF 400/401/403/404/429 responses. Supply trailing slashes.

## Authentication

```http
POST /api/auth/register/
Content-Type: application/json

{"username":"newmember","email":"member@example.test","password":"choose-a-strong-unique-password","first_name":"New"}
```

Registration returns 201 with account fields, never the password. Invalid/weak passwords return 400. Then obtain a token:

```http
POST /api/auth/token/
Content-Type: application/json

{"username":"newmember","password":"choose-a-strong-unique-password"}
```

Response: `{"token":"<issued-token>"}`. Include `Authorization: Token <issued-token>` on subsequent requests, including protected image requests. Tokens must be stored securely and transmitted over HTTPS. POST /api/auth/logout/ deletes the current user's token (204). Tokens are also revoked on password change; they do not expire automatically. Token logout does not log a browser session out.

The browsable API accepts session authentication. Session writes need a CSRF token. Mobile token authentication does not use CSRF cookies. WebSocket authentication currently supports browser sessions, not API tokens.

## Endpoints

| Method | Path | Purpose / body |
| --- | --- | --- |
| GET | /api/ | Authenticated browsable resource root |
| GET, PATCH, PUT | /api/me/ | Own profile: bio, location, website, profile_picture, cover_photo, is_private, default_visibility |
| GET | /api/users/?q=Prishu28 | Search people by name/username; blocked/inactive users excluded |
| GET | /api/users/{id}/ | Public profile details; email/password omitted |
| POST, DELETE | /api/users/{id}/follow/ | Follow/unfollow, idempotent |
| POST | /api/users/{id}/friend_request/ | Send friend request; receiver is the URL user |
| POST, DELETE | /api/users/{id}/block/ | Block/unblock; DELETE works even when blocked |
| GET | /api/posts/ | Paginated visibility-filtered posts |
| POST | /api/posts/ | content, optional image, visibility: public/friends/private |
| GET, PATCH, PUT, DELETE | /api/posts/{id}/ | Read visible post; only author edits/deletes |
| POST, DELETE | /api/posts/{id}/like/ | Add/remove own like, idempotent |
| GET, POST | /api/posts/{id}/comments/ | List visible comments or create with content |
| DELETE | /api/comments/{id}/ | Comment author or post author only |
| GET | /api/friend-requests/ | Only incoming/outgoing requests belonging to caller |
| GET, DELETE | /api/friend-requests/{id}/ | Read; cancel own pending or remove accepted friendship |
| POST | /api/friend-requests/{id}/respond/ | Receiver only: decision: accept/decline |
| GET | /api/notifications/ | Own visible inbox |
| GET | /api/notifications/{id}/ | Own notification |
| POST | /api/notifications/{id}/read/ | Mark one read |
| POST | /api/notifications/read_all/ | Mark all visible notifications read |
| POST | /api/reports/ | reason and exactly one of post/comment IDs |
| GET | /images/posts/{id}/ | Protected post image, same audience rules |
| GET | /images/profiles/{id}/{kind}/ | Protected profile_picture or cover_photo |
| GET | /health/ | Public infrastructure health, 200 or 503 |

For uploads use multipart/form-data. To remove an API image send null with a JSON PATCH. Text-only posts may omit image. Image extensions must match decoded JPEG/PNG/WebP, at most 5 MB and 20 MP.

Profile updates do not edit username/email/name through the API; the web settings form supports display-name changes. Returned profile and post image links point to permission-checked application routes, not public media files.

Post filters may be combined:

- q: substring in post content.
- author: numeric user ID.
- feed: following or friends (otherwise all visible posts).
- kind: photos.
- page: page number.

Example: `GET /api/posts/?feed=friends&kind=photos&page=1`.

Post representations include id, nested author, content, image_url, visibility, created_at, updated_at, like_count, comment_count and liked_by_me. Client-supplied author, timestamps, moderation state and aggregate counts cannot be assigned.

## WebSocket protocol

Connect with the website session cookie to ws://127.0.0.1:8000/ws/notifications/ locally, or wss://your-host/ws/notifications/ in production. Origins must match ALLOWED_HOSTS. Anonymous users are rejected.

Initial frame: `{"type":"connected"}`.

Event frame: `{"type":"notification","id":123,"message":"Prishu28 liked your post"}`.

Frames are server-to-client only. Clients cannot subscribe to another user's group or mark items read over the socket. Read state changes through the HTTP endpoints. Fetch the durable inbox after reconnect: transient frames missed offline are not replayed.

## Rate limits and examples

API login: 10/minute; anonymous API access: 60/hour; authenticated API: 600/hour. These are application limits, with Redis-backed counters when configured, and should be supplemented by ingress limits.

```python
import requests

base = "http://127.0.0.1:8000"
response = requests.post(base + "/api/auth/token/",
                         json={"username": "yashtri21", "password": "your-demo-password"})
response.raise_for_status()
session = requests.Session()
session.headers["Authorization"] = "Token " + response.json()["token"]
post = session.post(base + "/api/posts/",
                    json={"content": "Hello from mobile", "visibility": "friends"})
post.raise_for_status()
print(post.json())
```

`requests` is an example client dependency, not required by the server. Use HTTPS against production. Hidden and inaccessible post IDs return 404. A report against inaccessible content is rejected. A private profile does not grant access just because the caller follows it.
