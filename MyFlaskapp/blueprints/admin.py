from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import current_user
import MyFlaskapp.db as db
from MyFlaskapp.sync import sync_games
import os
import json

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
    cursor.execute("SELECT id, name, file_path, image_path FROM games")
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
        file_path = request.form.get('file_path', '').strip()
        image_path = request.form.get('image_path', '').strip()
        if not name:
            flash('Name is required', 'danger')
            return render_template('admin/games/create.html')
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO games (name, file_path, image_path) VALUES (%s, %s, %s)",
            (name, file_path, image_path)
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
        file_path = request.form.get('file_path', '').strip()
        image_path = request.form.get('image_path', '').strip()
        if not name:
            flash('Name is required', 'danger')
            cursor.close()
            conn.close()
            return render_template('admin/games/edit.html', game=game)
        upd = conn.cursor()
        upd.execute(
            "UPDATE games SET name = %s, file_path = %s, image_path = %s WHERE id = %s",
            (name, file_path, image_path, game_id)
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

@admin_bp.route('/leaderboard')
def leaderboard_management():
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) as total_users FROM users')
    stats = cursor.fetchone()
    
    cursor.execute('SELECT COUNT(*) as total_games FROM games')
    games_count = cursor.fetchone()
    stats['total_games'] = games_count['total_games']
    
    cursor.execute('SELECT COUNT(*) as total_scores FROM leaderboard_scores')
    scores_count = cursor.fetchone()
    stats['total_scores'] = scores_count['total_scores']
    
    cursor.execute('SELECT COUNT(*) as valid_scores FROM leaderboard_scores WHERE is_valid = TRUE')
    valid_count = cursor.fetchone()
    stats['valid_scores'] = valid_count['valid_scores']
    
    # Get recent scores with user and game info
    cursor.execute("""
        SELECT ls.*, u.firstname, u.lastname, g.name as game_name
        FROM leaderboard_scores ls
        JOIN users u ON ls.user_id = u.id
        JOIN games g ON ls.game_id = g.id
        ORDER BY ls.achieved_at DESC
        LIMIT 50
    """)
    scores = cursor.fetchall()
    
    # Get games for filters
    cursor.execute('SELECT * FROM games ORDER BY name')
    games = cursor.fetchall()
    
    # Get validation rules
    cursor.execute("""
        SELECT svr.*, g.name as game_name
        FROM score_validation_rules svr
        LEFT JOIN games g ON svr.game_id = g.id
        ORDER BY svr.is_active DESC, svr.game_id
    """)
    validation_rules = cursor.fetchall()
    
    # Get current rankings
    cursor.execute("""
        SELECT 
            g.name as game_name,
            MAX(CASE WHEN lr.rank_position = 1 THEN CONCAT(u.firstname, ' ', u.lastname) END) as first_player,
            MAX(CASE WHEN lr.rank_position = 1 THEN lr.score_value END) as first_score,
            MAX(CASE WHEN lr.rank_position = 2 THEN CONCAT(u.firstname, ' ', u.lastname) END) as second_player,
            MAX(CASE WHEN lr.rank_position = 2 THEN lr.score_value END) as second_score,
            MAX(CASE WHEN lr.rank_position = 3 THEN CONCAT(u.firstname, ' ', u.lastname) END) as third_player,
            MAX(CASE WHEN lr.rank_position = 3 THEN lr.score_value END) as third_score
        FROM leaderboard_rankings lr
        JOIN games g ON lr.game_id = g.id
        JOIN users u ON lr.user_id = u.id
        WHERE lr.time_period = 'all_time' AND lr.rank_position <= 3
        GROUP BY g.id, g.name
        ORDER BY g.name
    """)
    rankings = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin/leaderboard_management.html', 
                         stats=stats, scores=scores, games=games, 
                         validation_rules=validation_rules, rankings=rankings)


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

@admin_bp.route('/categories')
def categories():
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM game_categories ORDER BY name")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/categories/create', methods=['GET', 'POST'])
def create_category():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        if not name:
            flash('Category name is required', 'danger')
            return render_template('admin/create_category.html')
        
        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO game_categories (name, description) VALUES (%s, %s)", (name, description))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Category created successfully', 'success')
        return redirect(url_for('admin.categories'))
    
    return render_template('admin/create_category.html')

@admin_bp.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
def edit_category(category_id):
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM game_categories WHERE id = %s", (category_id,))
    category = cursor.fetchone()
    
    if not category:
        cursor.close()
        conn.close()
        flash('Category not found', 'danger')
        return redirect(url_for('admin.categories'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('Category name is required', 'danger')
            cursor.close()
            conn.close()
            return render_template('admin/edit_category.html', category=category)
        
        cursor.execute("UPDATE game_categories SET name = %s, description = %s WHERE id = %s", (name, description, category_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Category updated successfully', 'success')
        return redirect(url_for('admin.categories'))
    
    cursor.close()
    conn.close()
    return render_template('admin/edit_category.html', category=category)

@admin_bp.route('/categories/<int:category_id>/delete', methods=['POST'])
def delete_category(category_id):
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM game_category_association WHERE category_id = %s", (category_id,))
    cursor.execute("DELETE FROM game_categories WHERE id = %s", (category_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Category deleted successfully', 'success')
    return redirect(url_for('admin.categories'))

@admin_bp.route('/categories/<int:category_id>/games')
def category_games(category_id):
    conn = db.get_db()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM game_categories WHERE id = %s", (category_id,))
    category = cursor.fetchone()
    
    if not category:
        cursor.close()
        conn.close()
        flash('Category not found', 'danger')
        return redirect(url_for('admin.categories'))
    
    cursor.execute("""
        SELECT g.*, gca.is_associated
        FROM games g
        LEFT JOIN game_category_association gca ON g.id = gca.game_id AND gca.category_id = %s
        ORDER BY g.name
    """, (category_id,))
    games = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('admin/category_games.html', category=category, games=games)

@admin_bp.route('/categories/<int:category_id>/games', methods=['POST'])
def update_category_games(category_id):
    game_updates = request.get_json().get('games', [])
    
    conn = db.get_db()
    cursor = conn.cursor()
    
    # Clear existing associations
    cursor.execute("DELETE FROM game_category_association WHERE category_id = %s", (category_id,))
    
    # Add new associations
    for game_id in game_updates:
        cursor.execute("INSERT INTO game_category_association (category_id, game_id) VALUES (%s, %s)", (category_id, game_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({"status": "ok", "updated": len(game_updates)})
