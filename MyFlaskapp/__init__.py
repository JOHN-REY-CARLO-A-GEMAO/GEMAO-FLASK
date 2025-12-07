from flask import Flask, request, current_app
from werkzeug.exceptions import HTTPException
import logging
from logging.handlers import RotatingFileHandler
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask_login import LoginManager
from flask_mail import Mail
from .config import Config

mail = Mail()
login_manager = LoginManager()

def create_app(config: dict | None = None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config:
        app.config.update(config)

    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .blueprints.auth import auth_bp
    from .blueprints.admin import admin_bp
    from .blueprints.user import user_bp
    from .blueprints.main import main_bp
    from .blueprints.blog import blog_bp
    from .blueprints.api import api_bp
    from .leaderboard_routes import leaderboard_bp
    from .leaderboard_views import leaderboard_views_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(main_bp)
    app.register_blueprint(blog_bp, url_prefix='/blog')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(leaderboard_bp)
    app.register_blueprint(leaderboard_views_bp)
    
    # Initialize DB (Safe validation that tables exist)
    from .db import init_db_commands
    init_db_commands()

    try:
        if app.config.get('ENABLE_GAME_WATCHER'):
            from .sync import start_watcher
            start_watcher(app)
    except Exception:
        pass

    # Logging & error monitoring setup
    try:
        import os
        os.makedirs(app.config.get('LOG_DIR'), exist_ok=True)
        log_path = os.path.join(app.config.get('LOG_DIR'), 'app.log')
        handler = RotatingFileHandler(log_path, maxBytes=512_000, backupCount=5)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)
    except Exception:
        pass

    # In-memory error stats
    from collections import defaultdict
    app.extensions.setdefault('error_stats', {'counts': defaultdict(int)})

    def _record_error(kind: str, err: Exception):
        try:
            stats = app.extensions['error_stats']['counts']
            stats[kind] += 1
        except Exception:
            pass

    def _send_alert(subject: str, body: str):
        try:
            to_addr = app.config.get('ERROR_ALERT_EMAIL')
            if not to_addr:
                return
            from flask_mail import Message
            msg = Message(subject, recipients=[to_addr])
            msg.body = body
            mail.send(msg)
        except Exception:
            pass

    @app.context_processor
    def inject_csrf():
        def _gen():
            s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
            ident = 'anon'
            try:
                from flask import session
                ident = str(session.get('user_id') or 'anon')
            except Exception:
                pass
            return s.dumps(ident)
        return {'csrf_token': _gen}

    @app.errorhandler(Exception)
    def _handle_unexpected_error(e: Exception):
        if isinstance(e, HTTPException):
            return e
        app.logger.exception('Unhandled exception')
        _record_error('fatal', e)
        _send_alert('Critical Failure', f'Unhandled exception: {e!r}')
        return ('', 500)

    @app.before_request
    def _enforce_csrf():
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            if not app.config.get('ENABLE_CSRF', True):
                return None
            token = request.headers.get('X-CSRFToken') or request.form.get('csrf_token')
            if not token:
                return ('', 400)
            try:
                s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
                ident = s.loads(token, max_age=app.config.get('PERMANENT_SESSION_LIFETIME', 3600))
                from flask import session
                uid = str(session.get('user_id') or 'anon')
                if ident != uid:
                    return ('', 400)
            except (BadSignature, SignatureExpired):
                return ('', 400)
        return None

    @app.after_request
    def set_csp(resp):
        resp.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "img-src 'self' data: blob:; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "connect-src 'self'; "
            "font-src 'self' https://cdn.jsdelivr.net; "
        )
        return resp

    try:
        import os
        os.makedirs(app.config.get('UPLOAD_FOLDER_PROFILE'), exist_ok=True)
    except Exception:
        pass

    return app
