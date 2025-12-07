from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import MyFlaskapp.db as db
from MyFlaskapp import login_manager, mail
from MyFlaskapp.sessions import create_session, delete_session
from flask_mail import Message
import random
import datetime
import re
try:
    import mysql.connector as _mysql
    from mysql.connector import Error as MySQLError
except Exception:
    _mysql = None
    MySQLError = Exception

auth_bp = Blueprint('auth', __name__)

# Error handling reference:
# - RecoverableError: issues where the operation can be retried or alternate path exists (e.g., email send failure)
# - FatalError: unrecoverable failures such as database connection errors; these are logged and may trigger alerts
class RecoverableError(Exception):
    pass

class FatalError(Exception):
    pass

class User(UserMixin):
    def __init__(self, id, username, role, is_active):
        self.id = id
        self.username = username
        self.role = role
        self._is_active = bool(is_active)

    @property
    def is_active(self):
        return self._is_active

@login_manager.user_loader
def load_user(user_id):
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    if user_data:
        # Check active status
        return User(user_data['id'], user_data['username'], user_data['role'], user_data['is_active'])
    return None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated or session.get('loggedin'):
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = db.get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        
        if user_data and check_password_hash(user_data['password'], password):
            if not user_data['is_active']:
                flash('Invalid: Account not activated', 'warning')
                return redirect(url_for('auth.verify_otp', user_id=user_data['id']))
                
            user_obj = User(user_data['id'], user_data['username'], user_data['role'], user_data['is_active'])
            login_user(user_obj)
            session['loggedin'] = True
            session['user_id'] = user_obj.id
            session['username'] = user_obj.username
            session['role'] = user_obj.role
            
            session_token = create_session(user_obj.id, request.remote_addr, request.user_agent.string)
            session['session_token'] = session_token
            
            if user_obj.role == 'Admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
        
        cursor.close()
        conn.close()
        
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = (request.form.get('firstname') or '').strip()
        lastname = (request.form.get('lastname') or '').strip()
        username = (request.form.get('username') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''

        # Input validation
        errors = []
        if not firstname or not lastname:
            errors.append('First and Last name are required.')
        if not username or not re.match(r'^[A-Za-z0-9_\.\-]{3,32}$', username):
            errors.append('Username must be 3-32 chars (letters, numbers, .-_).')
        if not email or not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
            errors.append('Enter a valid email address.')
        if not password or len(password) < 8 or not re.search(r'[A-Za-z]', password) or not re.search(r'[0-9]', password):
            errors.append('Password must be at least 8 chars with letters and numbers.')

        if errors:
            for m in errors:
                flash(m, 'danger')
            return render_template('auth/register.html')

        try:
            hashed_password = generate_password_hash(password)
        except Exception as e:
            current_app.logger.exception('Password hashing failed')
            flash('Internal error while processing password.', 'danger')
            raise RecoverableError('hashing') from e

        conn = None
        cursor = None
        try:
            conn = db.get_db()
            if not conn:
                raise FatalError('db-connection')
            cursor = conn.cursor()

            # Check duplicates explicitly for user-friendly errors
            cur2 = conn.cursor(dictionary=True)
            cur2.execute("SELECT id FROM users WHERE username=%s OR email=%s", (username, email))
            existing = cur2.fetchone()
            cur2.close()
            if existing:
                flash('Username or Email already exists.', 'warning')
                return render_template('auth/register.html')

            cursor.execute(
                "INSERT INTO users (username, password, email, firstname, lastname, is_active) VALUES (%s, %s, %s, %s, %s, %s)",
                (username, hashed_password, email, firstname, lastname, False)
            )
            conn.commit()
            user_id = cursor.lastrowid

            # OTP Generation and persistence
            otp = str(random.randint(100000, 999999))
            cursor.execute("INSERT INTO otp_verification (user_id, otp_code) VALUES (%s, %s)", (user_id, otp))
            conn.commit()

            # Send Email (recoverable on failure)
            try:
                msg = Message('Verify your Account', recipients=[email])
                msg.body = f'Your OTP is: {otp}'
                mail.send(msg)
                flash('Registration successful! Please check email for OTP.', 'success')
            except Exception as e:
                current_app.logger.exception('OTP email send failed')
                flash('Email delivery failed. You can request a new OTP below.', 'warning')
            return redirect(url_for('auth.verify_otp', user_id=user_id))

        except MySQLError as e:
            try:
                code = getattr(e, 'errno', None)
                if code == 1062:
                    flash('Username or Email already exists.', 'warning')
                else:
                    flash('Database error occurred. Please try again.', 'danger')
                current_app.logger.exception('Database error during register')
            finally:
                try:
                    if conn:
                        conn.rollback()
                except Exception:
                    pass
        except RecoverableError:
            current_app.logger.exception('Recoverable error during register')
        except FatalError as e:
            current_app.logger.exception('Fatal error during register')
            from flask import current_app as _ca
            _stats = _ca.extensions.get('error_stats', {}).get('counts')
            if _stats is not None:
                _stats['fatal'] = _stats.get('fatal', 0) + 1
            flash('Critical system error. Please try again later.', 'danger')
            return ('', 500)
        except Exception:
            current_app.logger.exception('Unexpected error during register')
            flash('Unexpected error occurred.', 'danger')
        finally:
            try:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
            except Exception:
                pass

    return render_template('auth/register.html')

@auth_bp.route('/verify-otp/<int:user_id>', methods=['GET', 'POST'])
def verify_otp(user_id):
    if request.method == 'POST':
        otp_input = request.form.get('otp')
        
        conn = db.get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM otp_verification WHERE user_id = %s ORDER BY created_at DESC LIMIT 1", (user_id,))
        otp_record = cursor.fetchone()
        
        if otp_record and otp_record['otp_code'] == otp_input:
            cursor.execute("UPDATE users SET is_active = TRUE WHERE id = %s", (user_id,))
            conn.commit()
            flash('Account activated! You can now login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid OTP', 'danger')
            
        cursor.close()
        conn.close()
        
    return render_template('auth/verify_otp.html', user_id=user_id)

@auth_bp.route('/resend-otp/<int:user_id>', methods=['POST'])
def resend_otp(user_id: int):
    try:
        conn = db.get_db()
        if not conn:
            raise FatalError('db-connection')
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT email FROM users WHERE id=%s", (user_id,))
        row = cur.fetchone()
        if not row:
            flash('User not found.', 'danger')
            return redirect(url_for('auth.register'))

        otp = str(random.randint(100000, 999999))
        cur2 = conn.cursor()
        cur2.execute("INSERT INTO otp_verification (user_id, otp_code) VALUES (%s, %s)", (user_id, otp))
        conn.commit()
        cur2.close()

        try:
            msg = Message('Your new OTP', recipients=[row['email']])
            msg.body = f'Your OTP is: {otp}'
            mail.send(msg)
            flash('A new OTP has been sent to your email.', 'success')
        except Exception:
            current_app.logger.exception('Resend OTP email failed')
            flash('Failed to send OTP email. Please try again later.', 'warning')
        return redirect(url_for('auth.verify_otp', user_id=user_id))
    except FatalError:
        current_app.logger.exception('Fatal error in resend_otp')
        flash('Critical system error. Please try again later.', 'danger')
        return ('', 500)
    except Exception:
        current_app.logger.exception('Unexpected error in resend_otp')
        flash('Unexpected error occurred.', 'danger')
        return redirect(url_for('auth.verify_otp', user_id=user_id))

@auth_bp.route('/logout')
@login_required
def logout():
    session_token = session.get('session_token')
    if session_token:
        delete_session(session_token)
        session.pop('session_token', None)
        
    logout_user()
    session.pop('loggedin', None)
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('main.index'))
