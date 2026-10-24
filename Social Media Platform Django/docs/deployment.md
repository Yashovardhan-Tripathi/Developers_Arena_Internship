# Deployment guide

## Current status

Deployment is **pending at the user's explicit request**. These files prepare a release; no paid resources were provisioned, no remote repository was pushed, and no public endpoint has been verified. Docker is unavailable on this host, so the image and Compose runtime are not locally verified.

The project uses a long-running Daphne ASGI process so HTTP and WebSockets share the same origin. Do not replace it with a WSGI-only server.

## Railway

The supplied Dockerfile installs the exact dependency lock, collects static assets during image build, switches to an unprivileged user, and starts Daphne using PORT. railway.json specifies the Dockerfile builder, migration pre-deploy command, health check, and restart policy.

1. Push the source to a repository you control, or use an authenticated Railway CLI upload.
2. Create a Railway project and add PostgreSQL and Redis.
3. Add the application from the repository and use this directory as its root if it is nested in a larger repository.
4. Provision a **private** S3-compatible bucket, scoped credentials, and backups/versioning as appropriate.
5. Configure the variables below. Generate a real secret, for example with `python -c "import secrets; print(secrets.token_urlsafe(64))"`.
6. Deploy using the supplied Dockerfile. The pre-deploy command runs `python manage.py migrate --noinput` once before activation.
7. Generate the application domain and set exact ALLOWED_HOSTS/CSRF_TRUSTED_ORIGINS. Redeploy if variables change.
8. Run `python manage.py createsuperuser` in the service's authenticated shell. Do not run seed_demo in production.
9. Run the release verification below before treating the application as delivered.

| Variable | Production value |
| --- | --- |
| DEBUG | False |
| SECRET_KEY | Unique random value, at least 50 characters |
| DATABASE_URL | Railway PostgreSQL reference |
| REDIS_URL | Railway Redis reference |
| ALLOWED_HOSTS | Your exact app hostname,healthcheck.railway.app |
| CSRF_TRUSTED_ORIGINS | https://your-exact-app-hostname |
| SECURE_SSL_REDIRECT | True |
| USE_S3 | True |
| AWS_STORAGE_BUCKET_NAME | Private bucket name |
| AWS_ACCESS_KEY_ID | Scoped storage key, stored as a secret |
| AWS_SECRET_ACCESS_KEY | Scoped storage secret |
| AWS_S3_REGION_NAME | Bucket region |
| AWS_S3_ENDPOINT_URL | Optional S3-compatible endpoint, otherwise blank |

ALLOWED_HOSTS uses hostnames without schemes/paths. CSRF_TRUSTED_ORIGINS uses complete origins with https://. Health requests use Railway's healthcheck.railway.app hostname; include it in ALLOWED_HOSTS. /health/ is exempt from HTTPS redirect so the internal health probe can reach it. All normal traffic redirects to HTTPS. Only trust forwarded-proto headers from your hosting platform's ingress.

Media is read from the private bucket through permission-checked application routes; never make the bucket public or expose /media/ through an unprotected proxy. Bucket credentials need the appropriate GetObject, PutObject, DeleteObject and bucket-listing permissions for the selected storage backend. Verify actual upload/read/remove behavior against the real bucket before release.

The production check script validates settings with placeholder infrastructure URLs; it does not connect to or verify PostgreSQL, Redis, or a bucket.

## Heroku alternative

Use a Docker/container deployment with the supplied Dockerfile or the standard Python buildpack with requirements.txt and Procfile. The Procfile has a release migration command and a Daphne web command. Configure PostgreSQL, Redis, private S3, exact hostnames, and the same production environment variables.

The Heroku filesystem is ephemeral: never rely on local media or SQLite. Confirm current platform/buildpack Python support in the dashboard before deploying. No Heroku-specific runtime or release has been exercised in this workspace.

## Release verification

Run `python manage.py check --deploy` with the actual production variables and `python manage.py makemigrations --check --dry-run`. Back up the database before migrations.

Verify against the real HTTPS domain:

- /health/ returns 200 with working database and Redis.
- CSS/JS load and login, registration, logout and CSRF-protected forms work.
- Two independent users can create posts, like, comment, request/accept friendship and follow.
- A separate browser session receives a WebSocket notification; reconnect and inspect the durable inbox.
- Private-profile/friends/Only me posts remain unavailable to unauthorized accounts through web, API, direct IDs, search and image URLs.
- Upload an image, restart/redeploy the service, and confirm that image persists.
- A report can be reviewed by staff and hidden content disappears.
- API tokens work over TLS, then stop working after revocation/password change.
- Logs do not include secrets. Backups restore correctly. Alerts cover application errors and dependency failures.

Do not claim deployment complete until these checks have run on the live release.

## Operations

Use PostgreSQL backup and restore procedures and bucket lifecycle policies. Keep Redis private. Monitor errors, health, storage growth, slow queries, and WebSocket connections. Add ingress upload/body limits and trusted client-IP rate limiting. Configure platform health checks and TLS renewal.

For more instances, all application processes must share PostgreSQL, Redis and private media storage. Shared Redis cache supports rate-limit counters. The in-memory layer is for a single local process only.

Keep database migrations backwards compatible for rolling releases. To roll back code, redeploy the previous image after checking schema compatibility. Restore backups only under an explicit recovery plan; blindly reversing data migrations can lose user content.

## Reference documentation

- [Railway Django deployment](https://docs.railway.com/guides/django)
- [Railway config-as-code reference](https://docs.railway.com/config-as-code/reference)
- [Railway health checks](https://docs.railway.com/deployments/healthchecks)
- [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Channels channel layers](https://channels.readthedocs.io/en/stable/topics/channel_layers.html)
