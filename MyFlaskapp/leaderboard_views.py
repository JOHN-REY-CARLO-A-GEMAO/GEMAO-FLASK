"""
Leaderboard Views and Routes
Frontend routes for leaderboard pages
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime
import logging

from MyFlaskapp.leaderboard_models import LeaderboardScore, LeaderboardStats
from MyFlaskapp.db import get_db_connection

leaderboard_views_bp = Blueprint('leaderboard_views', __name__, url_prefix='/leaderboards')

logger = logging.getLogger(__name__)


@leaderboard_views_bp.route('/')
@login_required
def leaderboard_index():
    """Main leaderboard page"""
    try:
        # Get available games
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, name, description FROM games ORDER BY name")
        games = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Get form parameters
        game_id = request.args.get('game_id', type=int)
        time_period = request.args.get('time_period', 'all_time')
        difficulty = request.args.get('difficulty')
        limit = min(int(request.args.get('limit', 10)), 100)
        page = max(int(request.args.get('page', 1)), 1)
        
        selected_game = None
        scores = []
        game_stats = {}
        total_results = 0
        total_pages = 1
        current_page = page
        
        # Get leaderboard data if game is selected
        if game_id:
            # Find selected game
            selected_game = next((g for g in games if g['id'] == game_id), None)
            
            if selected_game:
                # Get scores
                scores = LeaderboardScore.get_top_scores(
                    game_id=game_id,
                    limit=limit,
                    time_period=time_period,
                    difficulty=difficulty
                )
                
                # Get game statistics
                game_stats = LeaderboardStats.get_game_stats(game_id)
                
                total_results = len(scores)
                
                # Calculate pagination (simplified for now)
                if total_results > limit:
                    total_pages = (total_results + limit - 1) // limit
        
        return render_template('leaderboards/leaderboard_complete.html',
                             games=games,
                             selected_game=selected_game,
                             scores=scores,
                             game_stats=game_stats,
                             time_period=time_period,
                             difficulty=difficulty,
                             limit=limit,
                             total_results=total_results,
                             total_pages=total_pages,
                             current_page=current_page)
        
    except Exception as e:
        logger.error(f"Error loading leaderboard: {str(e)}")
        return render_template('leaderboards/leaderboard_complete.html',
                             games=[],
                             selected_game=None,
                             scores=[],
                             game_stats={},
                             error="Failed to load leaderboard data")


@leaderboard_views_bp.route('/user/<int:user_id>')
@login_required
def user_leaderboard(user_id):
    """User's personal leaderboard page"""
    try:
        # Get user's personal bests
        personal_bests = LeaderboardScore.get_personal_bests(user_id)
        
        # Get user's recent scores
        recent_scores = LeaderboardScore.get_user_scores(user_id, limit=20)
        
        # Get user info
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT username, firstname, lastname FROM users WHERE id = %s", (user_id,))
        user_info = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not user_info:
            return render_template('errors/404.html'), 404
        
        # Get global stats for context
        global_stats = LeaderboardStats.get_global_stats()
        
        return render_template('leaderboards/user_leaderboard.html',
                             user_info=user_info,
                             personal_bests=personal_bests,
                             recent_scores=recent_scores,
                             global_stats=global_stats,
                             is_own_profile=current_user.id == user_id)
        
    except Exception as e:
        logger.error(f"Error loading user leaderboard: {str(e)}")
        return render_template('leaderboards/user_leaderboard.html',
                             user_info=None,
                             personal_bests=[],
                             recent_scores=[],
                             error="Failed to load user data")


@leaderboard_views_bp.route('/game/<int:game_id>')
@login_required
def game_leaderboard(game_id):
    """Detailed leaderboard for a specific game"""
    try:
        # Get game info
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM games WHERE id = %s", (game_id,))
        game = cursor.fetchone()
        
        if not game:
            return render_template('errors/404.html'), 404
        
        cursor.close()
        conn.close()
        
        # Get parameters
        time_period = request.args.get('time_period', 'all_time')
        difficulty = request.args.get('difficulty')
        limit = min(int(request.args.get('limit', 50)), 100)
        
        # Get leaderboard data
        scores = LeaderboardScore.get_top_scores(
            game_id=game_id,
            limit=limit,
            time_period=time_period,
            difficulty=difficulty
        )
        
        # Get game statistics
        game_stats = LeaderboardStats.get_game_stats(game_id)
        
        # Get current user's rank if logged in
        user_rank = None
        if current_user.is_authenticated:
            user_rank = LeaderboardScore.get_user_rank(current_user.id, game_id, time_period)
        
        return render_template('leaderboards/game_leaderboard.html',
                             game=game,
                             scores=scores,
                             game_stats=game_stats,
                             user_rank=user_rank,
                             time_period=time_period,
                             difficulty=difficulty,
                             limit=limit)
        
    except Exception as e:
        logger.error(f"Error loading game leaderboard: {str(e)}")
        return render_template('leaderboards/game_leaderboard.html',
                             game=None,
                             scores=[],
                             game_stats={},
                             error="Failed to load game data")


@leaderboard_views_bp.route('/compare')
@login_required
def compare_users():
    """User comparison page"""
    try:
        # Get available games
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, name FROM games ORDER BY name")
        games = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('leaderboards/compare.html', games=games)
        
    except Exception as e:
        logger.error(f"Error loading compare page: {str(e)}")
        return render_template('leaderboards/compare.html', games=[], error="Failed to load data")


@leaderboard_views_bp.route('/stats')
@login_required
def leaderboard_stats():
    """Global leaderboard statistics"""
    try:
        # Get global statistics
        global_stats = LeaderboardStats.get_global_stats()
        
        # Get top games by activity
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT g.id, g.name, COUNT(ls.id) as total_scores, 
                   AVG(ls.score_value) as avg_score,
                   MAX(ls.score_value) as high_score,
                   COUNT(DISTINCT ls.user_id) as unique_players
            FROM games g
            LEFT JOIN leaderboard_scores ls ON g.id = ls.game_id AND ls.is_valid = TRUE
            GROUP BY g.id, g.name
            HAVING total_scores > 0
            ORDER BY total_scores DESC
            LIMIT 10
        """)
        top_games = cursor.fetchall()
        
        # Get recent activity
        cursor.execute("""
            SELECT ls.score_value, ls.achieved_at, u.username, g.name as game_name
            FROM leaderboard_scores ls
            JOIN users u ON ls.user_id = u.id
            JOIN games g ON ls.game_id = g.id
            WHERE ls.is_valid = TRUE
            ORDER BY ls.achieved_at DESC
            LIMIT 20
        """)
        recent_activity = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('leaderboards/stats.html',
                             global_stats=global_stats,
                             top_games=top_games,
                             recent_activity=recent_activity)
        
    except Exception as e:
        logger.error(f"Error loading stats page: {str(e)}")
        return render_template('leaderboards/stats.html',
                             global_stats={},
                             top_games=[],
                             recent_activity=[],
                             error="Failed to load statistics")


# Error handlers for leaderboard views
@leaderboard_views_bp.errorhandler(404)
def leaderboard_not_found(error):
    return render_template('errors/404.html'), 404


@leaderboard_views_bp.errorhandler(500)
def leaderboard_internal_error(error):
    logger.error(f"Leaderboard internal error: {str(error)}")
    return render_template('errors/500.html'), 500
