from flask import render_template, request, redirect, url_for, flash, session
from . import admin_bp
from MyFlaskapp.db import get_db_connection
import datetime
import json
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('authenticated'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def generate_user_id():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    year = str(datetime.datetime.now().year)
    query = "SELECT user_id FROM user_tb WHERE user_id LIKE %s ORDER BY user_id DESC LIMIT 1"
    cursor.execute(query, (year + '%',))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        # result is like (user_id,)
        parts = result[0].split('-')
        if len(parts) > 1:
             last_num = int(parts[1])
             new_num = last_num + 1
        else:
             new_num = 1
    else:
        new_num = 1
    
    return f"{year}-{new_num:04d}"

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get users for dashboard
    cursor.execute('SELECT * FROM users ORDER BY created_at DESC LIMIT 10')
    users = cursor.fetchall()
    
    conn.close()
    return render_template('admin/dashboard.html', users=users)

@admin_bp.route('/leaderboard')
@login_required
def leaderboard_management():
    conn = get_db_connection()
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
    
    conn.close()
    
    return render_template('admin/leaderboard_management.html', 
                         stats=stats, scores=scores, games=games, 
                         validation_rules=validation_rules, rankings=rankings)

@admin_bp.route('/leaderboard/score/<int:score_id>/metrics', methods=['GET'])
@login_required
def get_score_metrics(score_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT ls.*, u.firstname, u.lastname, g.name as game_name
            FROM leaderboard_scores ls
            JOIN users u ON ls.user_id = u.id
            JOIN games g ON ls.game_id = g.id
            WHERE ls.id = %s
        """, (score_id,))
        
        score = cursor.fetchone()
        
        if not score:
            return {'error': 'Score not found'}, 404
        
        return {
            'metrics': score.get('additional_metrics', {}),
            'session_id': score.get('session_id'),
            'validation_hash': score.get('validation_hash'),
            'created_at': score.get('created_at').strftime('%Y-%m-%d %H:%M:%S') if score.get('created_at') else None,
            'updated_at': score.get('updated_at').strftime('%Y-%m-%d %H:%M:%S') if score.get('updated_at') else None
        }
        
    except Exception as e:
        return {'error': str(e)}, 500
    finally:
        conn.close()

@admin_bp.route('/leaderboard/score/<int:score_id>/validate', methods=['POST'])
@login_required
def validate_score(score_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE leaderboard_scores SET is_valid = TRUE WHERE id = %s", (score_id,))
        conn.commit()
        
        # Update rankings
        update_rankings(conn)
        
        return {'success': True, 'message': 'Score validated successfully'}
        
    except Exception as e:
        conn.rollback()
        return {'error': str(e)}, 500
    finally:
        conn.close()

@admin_bp.route('/leaderboard/score/<int:score_id>/invalidate', methods=['POST'])
@login_required
def invalidate_score(score_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE leaderboard_scores SET is_valid = FALSE WHERE id = %s", (score_id,))
        conn.commit()
        
        # Update rankings
        update_rankings(conn)
        
        return {'success': True, 'message': 'Score invalidated successfully'}
        
    except Exception as e:
        conn.rollback()
        return {'error': str(e)}, 500
    finally:
        conn.close()

@admin_bp.route('/leaderboard/score/<int:score_id>', methods=['DELETE'])
@login_required
def delete_score(score_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM leaderboard_scores WHERE id = %s", (score_id,))
        conn.commit()
        
        # Update rankings
        update_rankings(conn)
        
        return {'success': True, 'message': 'Score deleted successfully'}
        
    except Exception as e:
        conn.rollback()
        return {'error': str(e)}, 500
    finally:
        conn.close()

@admin_bp.route('/leaderboard/rules', methods=['POST'])
@login_required
def add_validation_rule():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        data = request.get_json()
        
        query = """
            INSERT INTO score_validation_rules 
            (game_id, max_score, min_score, max_playtime_seconds, score_multiplier, validation_rules, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(query, (
            data.get('game_id'),
            data.get('max_score'),
            data.get('min_score', 0),
            data.get('max_playtime_seconds'),
            data.get('score_multiplier', 1.0),
            '{}',  # Empty JSON for validation rules
            True
        ))
        
        conn.commit()
        return {'success': True, 'message': 'Validation rule added successfully'}
        
    except Exception as e:
        conn.rollback()
        return {'error': str(e)}, 500
    finally:
        conn.close()

@admin_bp.route('/leaderboard/rules/<int:rule_id>/toggle', methods=['POST'])
@login_required
def toggle_validation_rule(rule_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE score_validation_rules SET is_active = NOT is_active WHERE id = %s", (rule_id,))
        conn.commit()
        
        return {'success': True, 'message': 'Rule toggled successfully'}
        
    except Exception as e:
        conn.rollback()
        return {'error': str(e)}, 500
    finally:
        conn.close()

@admin_bp.route('/leaderboard/rules/<int:rule_id>', methods=['DELETE'])
@login_required
def delete_validation_rule(rule_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM score_validation_rules WHERE id = %s", (rule_id,))
        conn.commit()
        
        return {'success': True, 'message': 'Rule deleted successfully'}
        
    except Exception as e:
        conn.rollback()
        return {'error': str(e)}, 500
    finally:
        conn.close()

@admin_bp.route('/leaderboard/rules/<int:rule_id>', methods=['GET'])
@login_required
def get_validation_rule(rule_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT svr.*, g.name as game_name
            FROM score_validation_rules svr
            LEFT JOIN games g ON svr.game_id = g.id
            WHERE svr.id = %s
        """, (rule_id,))
        
        rule = cursor.fetchone()
        
        if not rule:
            return {'error': 'Rule not found'}, 404
        
        return rule
        
    except Exception as e:
        return {'error': str(e)}, 500
    finally:
        conn.close()

@admin_bp.route('/leaderboard/rules/<int:rule_id>', methods=['PUT'])
@login_required
def update_validation_rule(rule_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        data = request.get_json()
        
        query = """
            UPDATE score_validation_rules 
            SET game_id = %s, max_score = %s, min_score = %s, 
                max_playtime_seconds = %s, score_multiplier = %s, 
                validation_rules = %s, is_active = %s
            WHERE id = %s
        """
        
        cursor.execute(query, (
            data.get('game_id'),
            data.get('max_score'),
            data.get('min_score', 0),
            data.get('max_playtime_seconds'),
            data.get('score_multiplier', 1.0),
            data.get('validation_rules', '{}'),
            data.get('is_active', True),
            rule_id
        ))
        
        conn.commit()
        return {'success': True, 'message': 'Validation rule updated successfully'}
        
    except Exception as e:
        conn.rollback()
        return {'error': str(e)}, 500
    finally:
        conn.close()

@admin_bp.route('/leaderboard/rules/test', methods=['POST'])
@login_required
def test_validation_rule():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        data = request.get_json()
        game_id = data.get('game_id')
        score_value = data.get('score_value')
        playtime_seconds = data.get('playtime_seconds')
        difficulty_level = data.get('difficulty_level', 'medium')
        
        # Get validation rules for the game
        cursor.execute("""
            SELECT svr.*, g.name as game_name
            FROM score_validation_rules svr
            LEFT JOIN games g ON svr.game_id = g.id
            WHERE (svr.game_id = %s OR svr.game_id IS NULL) AND svr.is_active = TRUE
            ORDER BY svr.game_id DESC
        """, (game_id,))
        
        rules = cursor.fetchall()
        
        if not rules:
            return {
                'valid': True,
                'message': 'No validation rules defined - score accepted',
                'applied_rules': []
            }
        
        applied_rules = []
        
        for rule in rules:
            rule_name = rule['game_name'] or 'Global Rule'
            applied_rules.append(rule_name)
            
            # Basic validation
            if rule['min_score'] is not None and score_value < rule['min_score']:
                return {
                    'valid': False,
                    'message': f'Score below minimum ({rule["min_score"]}) for {rule_name}',
                    'applied_rules': applied_rules
                }
            
            if rule['max_score'] is not None and score_value > rule['max_score']:
                return {
                    'valid': False,
                    'message': f'Score above maximum ({rule["max_score"]}) for {rule_name}',
                    'applied_rules': applied_rules
                }
            
            if rule['max_playtime_seconds'] is not None and playtime_seconds > rule['max_playtime_seconds']:
                return {
                    'valid': False,
                    'message': f'Playtime exceeds maximum ({rule["max_playtime_seconds"]}s) for {rule_name}',
                    'applied_rules': applied_rules
                }
            
            # Advanced validation rules
            if rule['validation_rules']:
                try:
                    validation_rules = json.loads(rule['validation_rules'])
                    
                    # Check score per minute
                    if 'max_score_per_minute' in validation_rules and playtime_seconds > 0:
                        score_per_minute = (score_value / playtime_seconds) * 60
                        if score_per_minute > validation_rules['max_score_per_minute']:
                            return {
                                'valid': False,
                                'message': f'Score per minute ({score_per_minute:.2f}) exceeds maximum ({validation_rules["max_score_per_minute"]}) for {rule_name}',
                                'applied_rules': applied_rules
                            }
                    
                    # Check impossible threshold
                    if 'impossible_threshold' in validation_rules and score_value > validation_rules['impossible_threshold']:
                        return {
                            'valid': False,
                            'message': f'Score exceeds impossible threshold ({validation_rules["impossible_threshold"]}) for {rule_name}',
                            'applied_rules': applied_rules
                        }
                    
                except json.JSONDecodeError:
                    continue
        
        return {
            'valid': True,
            'message': 'Score passed all validation rules',
            'applied_rules': applied_rules
        }
        
    except Exception as e:
        return {'error': str(e)}, 500
    finally:
        conn.close()

def update_rankings(conn):
    """Helper function to update leaderboard rankings"""
    cursor = conn.cursor()
    
    try:
        # Clear existing all_time rankings
        cursor.execute("DELETE FROM leaderboard_rankings WHERE time_period = 'all_time'")
        
        # Insert new rankings
        query = """
            INSERT INTO leaderboard_rankings 
            (game_id, user_id, rank_position, score_value, achieved_at, time_period, period_start, period_end)
            SELECT 
                game_id,
                user_id,
                DENSE_RANK() OVER (PARTITION BY game_id ORDER BY score_value DESC) as rank_position,
                score_value,
                achieved_at,
                'all_time' as time_period,
                '2024-01-01 00:00:00' as period_start,
                '2099-12-31 23:59:59' as period_end
            FROM (
                SELECT 
                    user_id, 
                    game_id, 
                    MAX(score_value) as score_value,
                    MAX(achieved_at) as achieved_at
                FROM leaderboard_scores 
                WHERE is_valid = TRUE
                GROUP BY user_id, game_id
            ) best_scores
        """
        
        cursor.execute(query)
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()

@admin_bp.route('/users')
@login_required
def users_list():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM user_tb')
    users = cursor.fetchall()
    conn.close()
    return render_template('admin/users_list.html', users=users)

@admin_bp.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        user_id = generate_user_id()
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        birthdate = request.form['birthdate']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        mobile_number = request.form['mobile_number']
        address = request.form.get('address', '')
        user_type = request.form.get('user_type', 'user')

        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO user_tb (user_id, firstname, lastname, birthdate, username, password, email, mobile_number, address, user_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            cursor.execute(query, (user_id, firstname, lastname, birthdate, username, password, email, mobile_number, address, user_type))
            conn.commit()
            flash('User added successfully!', 'success')
            return redirect(url_for('admin.users_list'))
        except Exception as e:
            flash(f'Error adding user: {e}', 'danger')
        finally:
            conn.close()
            
    return render_template('admin/add_user.html')

@admin_bp.route('/update/<string:id>', methods=['GET', 'POST'])
@login_required
def update_user(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        birthdate = request.form['birthdate']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        mobile_number = request.form['mobile_number']
        address = request.form.get('address', '')
        user_type = request.form.get('user_type', 'user')
        
        query = """UPDATE user_tb SET 
            firstname=%s, lastname=%s, birthdate=%s, username=%s, 
            password=%s, email=%s, mobile_number=%s, address=%s, user_type=%s
            WHERE user_id=%s"""
            
        try:
            cursor.execute(query, (firstname, lastname, birthdate, username, password, email, mobile_number, address, user_type, id))
            conn.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('admin.users_list'))
        except Exception as e:
             flash(f'Error updating user: {e}', 'danger')
        finally:
             conn.close()
    else:
        cursor.execute("SELECT * FROM user_tb WHERE user_id=%s", (id,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('admin.users_list'))
            
        return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/delete', methods=['POST'])
@login_required
def delete_user():
    user_id = request.form.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM user_tb WHERE user_id=%s", (user_id,))
        conn.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting user: {e}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('admin.users_list'))
