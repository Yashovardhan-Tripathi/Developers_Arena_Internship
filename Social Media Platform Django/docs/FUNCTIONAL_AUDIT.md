# TimeConnector functionality audit

Date: 27 October 2026 (Asia/Kolkata).

## Result

The full local verification passed after correcting one reproduced API validation bug. The suite now has **63 passing tests** (8.510 seconds), up from 56. All five commands in `scripts/verify.py` exited with code 0; actual output is in [validation.txt](validation.txt). Dependency consistency (`pip check`) and Python source compilation also passed.

This is local functional evidence, not proof that every possible input, browser, deployment, or concurrent workload works.

## Coverage and evidence

| Area | Checks and result |
| --- | --- |
| Accounts | Registration, password strength, login, logout, session protection, password change, token issue/revocation passed. Added a password-change form workflow that verifies the session remains usable and the mobile token is removed. |
| Profiles | Profile updates, default privacy, protected avatar/cover upload, safe image widgets, and public-field filtering passed. |
| Posts | Create/edit/delete, ownership, empty content, escaping, photo upload/removal and protected image access passed. Added an HTML post/comment lifecycle. |
| Comments and likes | Idempotent likes, saved notifications, comment creation/deletion permissions, hidden/blocked comment filtering passed. |
| Social connections | Request/accept/decline/resend/cancel/unfriend, follow/unfollow, self-action rejection and bilateral blocks are covered by the suite. Added an HTML request/accept/follow/block/unblock workflow verifying relationship removal and profile access. |
| Privacy | Everyone/friends/Only me, private profiles, following without private access, revoked friendship, blocks and hidden-content rules passed. |
| Search and API | Authenticated API, pagination, search, friend/follow/photo filtering, author selection and invalid author input passed after the fix below. |
| Notifications | Recipient ownership, read state, privacy rechecks and three ASGI WebSocket tests passed (authenticated delivery, anonymous rejection, foreign-origin rejection). |
| Moderation | Added checks that staff hide actions resolve reports and record the reviewer/time, hide API content, and dismiss reports. Existing report-target checks passed. |
| Operational behavior | System checks, migration drift, static collection, production configuration checks, dependency consistency and compilation passed. Added login rate-limit and database-failure health checks (HTTP 429 and 503 respectively). |
| Demo data | Existing six seed/personalization tests passed in isolated databases. |

The seven added tests are in `tests/test_functional_audit.py`. Test mutations use isolated in-memory databases and storage; no real member content or relationships were edited for those workflows.

## Reproduced defect and correction

`GET /api/posts/?author=²` passed `str.isdigit()` but failed integer conversion in Django. An author consisting of 5,000 digits also passed that check but exceeded Python's conversion limit. Both caused unhandled exceptions instead of an input-validation response.

`api/views.py` now accepts only ASCII digits within the signed 64-bit ID range, checks length before conversion, and returns HTTP 400 for invalid input. Regression cases include Unicode digits, oversized strings, out-of-range IDs, negatives, decimals and normal author selection. The initial added-test run reproduced two errors; the final full run passed.

## Live browser checks

- Signed in through the rendered login form using the documented local evaluator account and reached the populated feed.
- Authenticated browser requests returned HTTP 200 for people, connections, notifications, settings, own profile, post detail, photo/friend/following feeds, post search, posts/users API lists and health (13 routes).
- The protected demo image decoded successfully in the rendered feed.
- Desktop feed measured 1,521 pixels of document width within a 1,536-pixel viewport.
- Mobile emulation at 390 × 844 measured 390 pixels of document width and visible mobile navigation; no horizontal overflow was observed on the feed.
- The inspected browser console had no warnings or errors at that point. This is a spot check, not a complete console history or browser compatibility test.

New screenshot export was denied by the browser tool's workspace-path configuration, so no new screenshot is claimed. Existing screenshots retain their original dates. Browser checks used existing content; mutation workflows were exercised in isolated automated tests.

## Environment and verification limits

- Restricted loopback sockets stalled Daphne startup in the sandbox. A traceback located the stall in Python's socketpair setup. The verification and local ASGI server worked when run with approved access outside the sandbox; no workaround was added to application code.
- Docker is unavailable on this host, so Docker/Compose runtime behavior remains unverified.
- Real PostgreSQL, Redis and private S3 integration, concurrency/locking, public TLS/WebSocket behavior and cloud deployment remain unverified. `check --deploy` used placeholders and did not establish these connections.
- Git status/diff checks were unavailable: this project has no local `.git` entry, and Git discovery fails while attempting to access the parent internship checkout. No commit or push was performed.
- No load benchmark, penetration test, automated accessibility audit or cross-browser matrix was performed.
- Optional chat, groups, events, email verification, self-service password recovery and expiring API tokens remain outside the implemented feature set.
- Existing feed queries prefetch all visible comments for each page of posts; high-volume performance is not established by these tests.

## Repeat

```powershell
.\.venv\Scripts\python.exe scripts\verify.py
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m compileall -q api friends notifications posts social_platform users tests scripts
```

The raw verification log is overwritten by each verification run. Review this report alongside the current source and log.
