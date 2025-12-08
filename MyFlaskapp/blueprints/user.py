from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask import send_from_directory, current_app
from flask_login import current_user
import MyFlaskapp.db as db
import os
import sys
import subprocess
from MyFlaskapp import preferences

user_bp = Blueprint('user', __name__)

@user_bp.before_request
def require_login_flag():
    if not getattr(current_user, 'is_authenticated', False):
        return redirect(url_for('auth.login'))

GAMES = [
    {'name': 'Naruto Shuriken Toss', 'file': 'naruto_shuriken_toss.py', 'desc': 'Test your aim!'},
    {'name': 'Rasengan Training', 'file': 'rasengan_training.py', 'desc': 'Control your chakra.'},
    {'name': 'Chunin Exam Battle', 'file': 'chunin_exam.py', 'desc': 'Strategy battle.'},
    {'name': 'Shadow Clone Dodge', 'file': 'shadow_clone.py', 'desc': 'Avoid obstacles.'},
    {'name': 'Kunai Reflex', 'file': 'kunai_reflex.py', 'desc': 'Test your speed.'},
    {'name': 'Ninjutsu Memory', 'file': 'ninjutsu_memory.py', 'desc': 'Match the signs.'},
    {'name': 'Akatsuki Maze', 'file': 'akatsuki_maze.py', 'desc': 'Escape the hideout.'},
    {'name': 'Sakura Healing', 'file': 'sakura_healing.py', 'desc': 'Heal the wounded.'},
    {'name': 'Kakashi Pattern', 'file': 'kakashi_pattern.py', 'desc': 'Follow the pattern.'},
    {'name': 'Naruto Runner', 'file': 'naruto_runner.py', 'desc': 'Run forever!'}
]

@user_bp.route('/dashboard')
def dashboard():
    uid = getattr(current_user, 'id', None) or session.get('user_id')
    conn = db.get_db()
    cur = conn.cursor(dictionary=True)
    
    # Get games with access
    cur.execute(
        """
        SELECT g.id, g.name, g.description, g.file_path,
               COALESCE(ga.is_allowed, FALSE) AS is_allowed
        FROM games g
        LEFT JOIN game_access ga ON ga.game_id = g.id AND ga.user_id = %s
        ORDER BY g.name
        """,
        (uid,)
    )
    games = cur.fetchall()
    
    # Get personal bests
    cur.execute(
        """
        SELECT upb.*, g.name as game_name
        FROM user_personal_bests upb
        JOIN games g ON upb.game_id = g.id
        WHERE upb.user_id = %s
        ORDER BY upb.achieved_at DESC
        LIMIT 10
        """,
        (uid,)
    )
    personal_bests = cur.fetchall()
    
    # Get current points
    cur.execute("SELECT points FROM user_points WHERE user_id = %s", (uid,))
    points_result = cur.fetchone()
    current_points = points_result['points'] if points_result else 0
    
    cur.close()
    conn.close()
    return render_template('user/dashboard.html', games=games, personal_bests=personal_bests, current_points=current_points)

@user_bp.route('/play/<path:game_file>')
def play_game(game_file):
    uid = getattr(current_user, 'id', None) or session.get('user_id')
    conn = db.get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT COALESCE(ga.is_allowed, FALSE) AS is_allowed
        FROM games g
        LEFT JOIN game_access ga ON ga.game_id = g.id AND ga.user_id = %s
        WHERE g.file_path = %s
        """,
        (uid, game_file)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        flash('Game not found.', 'danger')
        return redirect(url_for('user.dashboard'))
    if not bool(row.get('is_allowed')):
        flash('Access to this game is disabled for your account.', 'warning')
        return redirect(url_for('user.dashboard'))

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'games'))
    script_path = os.path.abspath(os.path.join(base_dir, game_file))
    if not script_path.startswith(base_dir) or not os.path.exists(script_path):
        flash('Unable to launch game.', 'danger')
        return redirect(url_for('user.dashboard'))

    try:
        flags = 0
        if hasattr(subprocess, 'CREATE_NO_WINDOW'):
            flags |= subprocess.CREATE_NO_WINDOW
        if hasattr(subprocess, 'DETACHED_PROCESS'):
            flags |= subprocess.DETACHED_PROCESS
        subprocess.Popen([sys.executable, script_path], cwd=base_dir, creationflags=flags or 0)
        flash('Launching game...', 'success')
    except Exception:
        flash('Failed to launch game.', 'danger')
    return redirect(url_for('user.dashboard'))

@user_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    uid = getattr(current_user, 'id', None) or session.get('user_id')
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        middlename = request.form.get('middlename')
        birthdate = request.form.get('birthdate')
        contact = request.form.get('contact')
        email_notifications = 'email_notifications' in request.form
        sms_notifications = 'sms_notifications' in request.form
        
        # Calculate Age (Simple)
        from datetime import datetime
        age = 0
        if birthdate:
            bdate = datetime.strptime(birthdate, '%Y-%m-%d')
            today = datetime.today()
            if bdate > today:
                flash('Birthdate cannot be in the future.', 'danger')
                return redirect(url_for('user.profile'))
            age = today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))
        
        cursor.execute("""
            UPDATE users SET middlename=%s, birthday=%s, age=%s, contact_number=%s 
            WHERE id=%s
        """, (middlename, birthdate, age, contact, uid))
        conn.commit()

        preferences.update_notification_preferences(uid, email_notifications, sms_notifications)
        
        flash('Profile updated!', 'success')
        return redirect(url_for('user.profile'))

    cursor.execute("SELECT * FROM users WHERE id = %s", (uid,))
    user_info = cursor.fetchone()
    user_preferences = preferences.get_notification_preferences(uid)
    cursor.close()
    conn.close()
    
    return render_template('user/profile.html', user=user_info, preferences=user_preferences)

@user_bp.route('/profile-picture/<int:user_id>')
def get_profile_picture(user_id: int):
    import MyFlaskapp.db as db
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT profile_picture_path FROM users WHERE id=%s", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row or not row.get('profile_picture_path'):
        return ('', 404)
    folder = current_app.config.get('UPLOAD_FOLDER_PROFILE')
    return send_from_directory(folder, row['profile_picture_path'])

@user_bp.route('/points-history')
def points_history():
    uid = getattr(current_user, 'id', None) or session.get('user_id')
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)
    
    # Get current points
    cursor.execute("SELECT points FROM user_points WHERE user_id = %s", (uid,))
    current_points = cursor.fetchone()
    current_points = current_points['points'] if current_points else 0
    
    # Get transaction history
    cursor.execute("""
        SELECT points, reason, created_at 
        FROM points_transactions 
        WHERE user_id = %s 
        ORDER BY created_at DESC 
        LIMIT 50
    """, (uid,))
    transactions = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('user/points_history.html', 
                         current_points=current_points, 
                         transactions=transactions)
