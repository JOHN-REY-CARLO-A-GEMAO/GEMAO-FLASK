import os
from pathlib import Path
def _load_env():
    root = Path(__file__).resolve().parents[1]
    env_path = root / '.env'
    if not env_path.exists():
        return
    try:
        with env_path.open('r', encoding='utf-8') as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith('#'):
                    continue
                if '=' in s:
                    k, v = s.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())
    except Exception:
        pass

_load_env()

class Config:
    # General App Config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    # MySQL
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'gemao_db')

    # Mail Config
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT')) if os.environ.get('MAIL_PORT') else None
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') == 'True' if os.environ.get('MAIL_USE_TLS') else None

    # ❗ These should be ENV keys, not actual email & password
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # Sessions (1 hour)
    PERMANENT_SESSION_LIFETIME = 3600
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')

    # Uploads
    BASE_DIR = Path(__file__).resolve().parents[1]
    UPLOAD_FOLDER_PROFILE = os.environ.get('UPLOAD_FOLDER_PROFILE') or str(BASE_DIR / 'MyFlaskapp' / 'uploads' / 'profile_pictures')

    # Watcher control
    ENABLE_GAME_WATCHER = os.environ.get('ENABLE_GAME_WATCHER', 'False') == 'True'
    ENABLE_CSRF = os.environ.get('ENABLE_CSRF', 'True') == 'True'

    # Error monitoring / logging
    LOG_DIR = os.environ.get('LOG_DIR') or str(BASE_DIR / 'logs')
    ERROR_ALERT_EMAIL = os.environ.get('ERROR_ALERT_EMAIL')
