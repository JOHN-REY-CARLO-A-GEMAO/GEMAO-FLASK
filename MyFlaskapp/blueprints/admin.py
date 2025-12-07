from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import current_user
import MyFlaskapp.db as db
from MyFlaskapp.sync import sync_games
import os
import json
import MyFlaskapp.api_key_manager as api_key_manager
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
def require_admin():
    if not getattr(current_user, 'is_authenticated', False):
        return redirect(url_for('auth.login'))
    role = getattr(current_user, 'role', None)
    if role != 'Admin':
        flash('Access Denied', 'danger')
        return redirect(url_for('user.dashboard'))

@admin_bp.route('/dashboard')
def dashboard():
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/dashboard.html', users=users)

@admin_bp.route('/games')
def games_index():
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, description, file_path, image_path FROM games")
    games = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/games/index.html', games=games)

@admin_bp.route('/games/sync', methods=['POST'])
def games_sync():
    actor_id = getattr(current_user, 'id', None) or session.get('user_id')
    res = sync_games(actor_id)
    flash(f"Sync completed: added {res['inserted']}, updated {res['updated']}, skipped {res['skipped']}, errors {res['errors']}", 'info')
    return redirect(url_for('admin.games_index'))

@admin_bp.route('/games/create', methods=['GET', 'POST'])
def games_create():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        file_path = request.form.get('file_path', '').strip()
        image_path = request.form.get('image_path', '').strip()
        if not name:
            flash('Name is required', 'danger')
            return render_template('admin/games/create.html')
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO games (name, description, file_path, image_path) VALUES (%s, %s, %s, %s)",
            (name, description, file_path, image_path)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Game created', 'success')
        return redirect(url_for('admin.games_index'))
    return render_template('admin/games/create.html')

@admin_bp.route('/games/<int:game_id>/edit', methods=['GET', 'POST'])
def games_edit(game_id):
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM games WHERE id = %s", (game_id,))
    game = cursor.fetchone()
    if not game:
        cursor.close()
        conn.close()
        flash('Game not found', 'danger')
        return redirect(url_for('admin.games_index'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        file_path = request.form.get('file_path', '').strip()
        image_path = request.form.get('image_path', '').strip()
        if not name:
            flash('Name is required', 'danger')
            cursor.close()
            conn.close()
            return render_template('admin/games/edit.html', game=game)
        upd = conn.cursor()
        upd.execute(
            "UPDATE games SET name = %s, description = %s, file_path = %s, image_path = %s WHERE id = %s",
            (name, description, file_path, image_path, game_id)
        )
        conn.commit()
        upd.close()
        cursor.close()
        conn.close()
        flash('Game updated', 'success')
        return redirect(url_for('admin.games_index'))
    cursor.close()
    conn.close()
    return render_template('admin/games/edit.html', game=game)

@admin_bp.route('/games/<int:game_id>/delete', methods=['POST'])
def games_delete(game_id):
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM games WHERE id = %s", (game_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Game deleted', 'success')
    return redirect(url_for('admin.games_index'))

@admin_bp.route('/settings', methods=['GET'])
def settings():
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM games ORDER BY name")
    games = cursor.fetchall()
    cursor.close()
    conn.close()
    base = os.path.dirname(__file__)
    settings_path = os.path.abspath(os.path.join(base, '..', 'games', 'audio_settings.json'))
    data = {}
    try:
        if os.path.exists(settings_path):
            with open(settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f) or {}
    except Exception:
        data = {}
    return render_template('admin/settings.html', games=games, audio_settings=data)

@admin_bp.route('/settings/audio', methods=['POST'])
def settings_audio_update():
    payload = request.get_json(silent=True) or {}
    master = payload.get('master')
    ambient = payload.get('ambient')
    per_game = payload.get('per_game') or {}
    base = os.path.dirname(__file__)
    settings_path = os.path.abspath(os.path.join(base, '..', 'games', 'audio_settings.json'))
    current = {}
    try:
        if os.path.exists(settings_path):
            with open(settings_path, 'r', encoding='utf-8') as f:
                current = json.load(f) or {}
    except Exception:
        current = {}
    if isinstance(master, (int, float)):
        current['master'] = max(0.0, min(1.0, float(master)))
    if isinstance(ambient, (int, float)):
        current['ambient'] = max(0.0, min(1.0, float(ambient)))
    if isinstance(per_game, dict):
        current['games'] = current.get('games') or {}
        for k, v in per_game.items():
            try:
                current['games'][str(k)] = max(0.0, min(1.0, float(v)))
            except Exception:
                continue
    try:
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(current, f)
    except Exception:
        return jsonify({'ok': False}), 500
    return jsonify({'ok': True})

@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('User deleted', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/toggle_status/<int:user_id>', methods=['POST'])
def toggle_status(user_id):
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_active = NOT is_active WHERE id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('User status updated', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/user/<int:user_id>/game-access', methods=['GET'])
def user_game_access(user_id):
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        conn.close()
        return jsonify({"error": "User not found"}), 404

    cursor.execute(
        """
        SELECT g.id, g.name,
               COALESCE(ga.is_allowed, FALSE) AS is_allowed
        FROM games g
        LEFT JOIN game_access ga ON ga.game_id = g.id AND ga.user_id = %s
        ORDER BY g.name
        """,
        (user_id,)
    )
    games = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"user": {"id": user["id"], "username": user["username"]}, "games": games})

@admin_bp.route('/user/<int:user_id>/game-access', methods=['POST'])
def update_user_game_access(user_id):
    role = getattr(current_user, 'role', None) or session.get('role')
    if role != 'Admin':
        return jsonify({"error": "Unauthorized"}), 403

    payload = request.get_json(silent=True) or {}
    updates = payload.get('updates', [])

    conn = db.get_db()
    check = conn.cursor()
    check.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    exists = check.fetchone()
    if not exists:
        check.close()
        conn.close()
        return jsonify({"error": "User not found"}), 404
    check.close()

    cursor = conn.cursor()
    changed = 0
    changes = []
    for item in updates:
        try:
            game_id = int(item.get('game_id'))
            is_allowed = bool(item.get('is_allowed'))
        except Exception:
            continue
        cursor.execute(
            """
            INSERT INTO game_access (user_id, game_id, is_allowed)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE is_allowed = VALUES(is_allowed)
            """,
            (user_id, game_id, is_allowed)
        )
        changed += 1
        changes.append({"game_id": game_id, "is_allowed": is_allowed})
    conn.commit()
    cursor.close()
    conn.close()

    actor_id = getattr(current_user, 'id', None) or session.get('user_id')
    try:
        db.log_audit_action(actor_id, user_id, 'update_game_access', str(changes))
    except Exception:
        pass

    return jsonify({"status": "ok", "updated": changed})

@admin_bp.route('/api_keys', methods=['GET'])
def api_keys():
    user_id = getattr(current_user, 'id', None)
    if not user_id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    api_keys_list = api_key_manager.get_user_api_keys(user_id)
    return render_template('admin/api_keys.html', api_keys=api_keys_list)

@admin_bp.route('/api_keys/create', methods=['POST'])
def create_api_key():
    user_id = getattr(current_user, 'id', None)
    if not user_id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))

    target_user_id = request.form.get('user_id', type=int)
    permissions = request.form.get('permissions')
    expires_at_str = request.form.get('expires_at')
    expires_at = None
    if expires_at_str:
        try:
            expires_at = datetime.fromisoformat(expires_at_str)
        except ValueError:
            flash('Invalid date format for expiration.', 'danger')
            return redirect(url_for('admin.api_keys'))

    try:
        raw_key, _ = api_key_manager.create_api_key(target_user_id or user_id, permissions, expires_at)
        flash(f'API Key created: {raw_key}', 'success')
    except Exception as e:
        flash(f'Error creating API Key: {e}', 'danger')
    
    return redirect(url_for('admin.api_keys'))

@admin_bp.route('/api_keys/<int:key_id>/delete', methods=['POST'])
def delete_api_key(key_id):
    user_id = getattr(current_user, 'id', None)
    if not user_id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('auth.login'))
    
    key_data = api_key_manager.get_api_key(key_id) # This needs to be by key_id, not key_hash
    if key_data and key_data['user_id'] != user_id: # Only allow admin to delete his own keys or general keys
        flash('Unauthorized to delete this API key.', 'danger')
        return redirect(url_for('admin.api_keys'))

    if api_key_manager.delete_api_key(key_id):
        flash('API Key deleted.', 'success')
    else:
        flash('Error deleting API Key.', 'danger')
    
    return redirect(url_for('admin.api_keys'))
