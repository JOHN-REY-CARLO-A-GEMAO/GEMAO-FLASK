## 2025-12-07

- Fixed a bug in the `_update_personal_best` method in `MyFlaskapp/leaderboard_models.py` where the `average_score` was not being calculated correctly.
- Enabled global CSRF protection via `Flask-WTF` and injected `csrf_token()` for templates.
- Secured session cookies (`Secure`, `HttpOnly`, `SameSite=Lax`) and added `ENABLE_GAME_WATCHER` env toggle.
- Removed session trust for access control; enforced `Flask-Login` authentication and role checks.
- Converted unsafe admin GET actions to POST with CSRF and fixed role casing to `'Admin'` in templates.
- Added CSRF headers to admin settings AJAX; added hidden tokens to all forms.
- Strengthened DB guard to raise clearly when unavailable.
- Added unit tests to verify CSRF enforcement on admin endpoints.

## 2025-12-06

- Updated `MyFlaskapp/config.py` to remove hardcoded mail credentials and to use environment variables: `MAIL_USERNAME`, `MAIL_PASSWORD`, and `MAIL_DEFAULT_SENDER`.
- Kept `MAIL_SERVER`, `MAIL_PORT`, and `MAIL_USE_TLS` environment-driven; added a safe default sender `noreply@gemao.com`.
- No dependency changes required; `Flask-Mail` and `mysql-connector-python` already present in `requirements.txt`.
- Restarted development server and ran unit tests to verify configuration loads correctly.
