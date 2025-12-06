## 2025-12-06

- Updated `MyFlaskapp/config.py` to remove hardcoded mail credentials and to use environment variables: `MAIL_USERNAME`, `MAIL_PASSWORD`, and `MAIL_DEFAULT_SENDER`.
- Kept `MAIL_SERVER`, `MAIL_PORT`, and `MAIL_USE_TLS` environment-driven; added a safe default sender `noreply@gemao.com`.
- No dependency changes required; `Flask-Mail` and `mysql-connector-python` already present in `requirements.txt`.
- Restarted development server and ran unit tests to verify configuration loads correctly.
