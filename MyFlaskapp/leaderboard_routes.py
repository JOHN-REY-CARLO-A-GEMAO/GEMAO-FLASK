"""
Leaderboard API Routes
RESTful endpoints for leaderboard functionality
"""

from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from datetime import datetime
import logging

from MyFlaskapp.leaderboard_models import LeaderboardScore, LeaderboardStats

leaderboard_bp = Blueprint('leaderboard', __name__, url_prefix='/api/leaderboard')

# Configure logging
logger = logging.getLogger(__name__)


@leaderboard_bp.route('/scores', methods=['POST'])
@login_required
def submit_score():
    """Submit a new score"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['game_id', 'score_value']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        game_id = int(data['game_id'])
        score_value = float(data['score_value'])
        playtime_seconds = data.get('playtime_seconds', 0)
        difficulty_level = data.get('difficulty_level', 'medium')
        additional_metrics = data.get('additional_metrics', {})
        
        # Validate score
        if not LeaderboardScore.validate_score(game_id, score_value, playtime_seconds):
            return jsonify({'error': 'Score validation failed'}), 400
        
        # Create score
        score = LeaderboardScore.create_score(
            user_id=current_user.id,
            game_id=game_id,
            score_value=score_value,
            playtime_seconds=playtime_seconds,
            difficulty_level=difficulty_level,
            additional_metrics=additional_metrics
        )
        
        logger.info(f"Score submitted: User {current_user.id}, Game {game_id}, Score {score_value}")
        
        return jsonify({
            'success': True,
            'score_id': score.id,
            'rank_position': score.rank_position,
            'message': 'Score submitted successfully'
        }), 201
        
    except ValueError as e:
        return jsonify({'error': 'Invalid data format'}), 400
    except Exception as e:
        logger.error(f"Error submitting score: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@leaderboard_bp.route('/games/<int:game_id>/top', methods=['GET'])
def get_top_scores(game_id):
    """Get top scores for a specific game"""
    try:
        limit = min(int(request.args.get('limit', 10)), 100)  # Max 100 results
        time_period = request.args.get('time_period', 'all_time')
        difficulty = request.args.get('difficulty')
        
        # Validate time period
        valid_periods = ['daily', 'weekly', 'all_time']
        if time_period not in valid_periods:
            return jsonify({'error': 'Invalid time period'}), 400
        
        # Validate difficulty
        valid_difficulties = ['easy', 'medium', 'hard', 'expert']
        if difficulty and difficulty not in valid_difficulties:
            return jsonify({'error': 'Invalid difficulty level'}), 400
        
        scores = LeaderboardScore.get_top_scores(
            game_id=game_id,
            limit=limit,
            time_period=time_period,
            difficulty=difficulty
        )
        
        # Format response
        result = {
            'game_id': game_id,
            'time_period': time_period,
            'difficulty': difficulty,
            'total_results': len(scores),
            'scores': []
        }
        
        for i, score in enumerate(scores, 1):
            score_data = {
                'rank': i,
                'user_id': score.user_id,
                'username': score.username,
                'firstname': score.firstname,
                'lastname': score.lastname,
                'score_value': float(score.score_value),
                'achieved_at': score.achieved_at.isoformat() if score.achieved_at else None,
                'difficulty_level': score.difficulty_level,
                'playtime_seconds': score.playtime_seconds
            }
            
            # Add additional metrics if available
            if score.additional_metrics:
                score_data['additional_metrics'] = score.additional_metrics
            
            result['scores'].append(score_data)
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': 'Invalid parameters'}), 400
    except Exception as e:
        logger.error(f"Error getting top scores: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@leaderboard_bp.route('/games/<int:game_id>/rank/<int:user_id>', methods=['GET'])
def get_user_rank(game_id, user_id):
    """Get a specific user's rank for a game"""
    try:
        time_period = request.args.get('time_period', 'all_time')
        
        # Validate time period
        valid_periods = ['daily', 'weekly', 'all_time']
        if time_period not in valid_periods:
            return jsonify({'error': 'Invalid time period'}), 400
        
        rank_info = LeaderboardScore.get_user_rank(user_id, game_id, time_period)
        
        if not rank_info:
            return jsonify({'error': 'User not found in leaderboard'}), 404
        
        result = {
            'game_id': game_id,
            'user_id': user_id,
            'time_period': time_period,
            'rank_position': rank_info['rank_position'],
            'score_value': float(rank_info['score_value']),
            'achieved_at': rank_info['achieved_at'].isoformat() if rank_info['achieved_at'] else None,
            'total_players': rank_info['total_players'],
            'percentile': round((rank_info['total_players'] - rank_info['rank_position']) / rank_info['total_players'] * 100, 2)
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting user rank: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@leaderboard_bp.route('/users/<int:user_id>/scores', methods=['GET'])
def get_user_scores(user_id):
    """Get scores for a specific user"""
    try:
        game_id = request.args.get('game_id', type=int)
        limit = min(int(request.args.get('limit', 50)), 200)  # Max 200 results
        
        scores = LeaderboardScore.get_user_scores(user_id, game_id, limit)
        
        result = {
            'user_id': user_id,
            'game_id': game_id,
            'total_results': len(scores),
            'scores': []
        }
        
        for score in scores:
            score_data = {
                'score_id': score.id,
                'game_id': score.game_id,
                'game_name': getattr(score, 'game_name', None),
                'score_value': float(score.score_value),
                'rank_position': score.rank_position,
                'achieved_at': score.achieved_at.isoformat() if score.achieved_at else None,
                'difficulty_level': score.difficulty_level,
                'playtime_seconds': score.playtime_seconds,
                'is_valid': score.is_valid
            }
            
            if score.additional_metrics:
                score_data['additional_metrics'] = score.additional_metrics
            
            result['scores'].append(score_data)
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': 'Invalid parameters'}), 400
    except Exception as e:
        logger.error(f"Error getting user scores: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@leaderboard_bp.route('/users/<int:user_id>/personal-bests', methods=['GET'])
def get_personal_bests(user_id):
    """Get user's personal best scores"""
    try:
        personal_bests = LeaderboardScore.get_personal_bests(user_id)
        
        result = {
            'user_id': user_id,
            'total_games': len(personal_bests),
            'personal_bests': []
        }
        
        for best in personal_bests:
            best_data = {
                'game_id': best['game_id'],
                'game_name': best['game_name'],
                'game_description': best['description'],
                'best_score': float(best['best_score']),
                'best_rank': best['best_rank'],
                'achieved_at': best['achieved_at'].isoformat() if best['achieved_at'] else None,
                'total_plays': best['total_plays'],
                'average_score': float(best['average_score']) if best['average_score'] else None,
                'last_played_at': best['last_played_at'].isoformat() if best['last_played_at'] else None
            }
            
            result['personal_bests'].append(best_data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting personal bests: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@leaderboard_bp.route('/games/<int:game_id>/stats', methods=['GET'])
def get_game_stats(game_id):
    """Get statistics for a specific game"""
    try:
        stats = LeaderboardStats.get_game_stats(game_id)
        
        # Format statistics
        result = {
            'game_id': game_id,
            'total_plays': stats['total_plays'],
            'unique_players': stats['unique_players'],
            'average_score': float(stats['avg_score']) if stats['avg_score'] else 0,
            'high_score': float(stats['high_score']) if stats['high_score'] else 0,
            'low_score': float(stats['low_score']) if stats['low_score'] else 0,
            'plays_today': stats['plays_today'],
            'difficulty_distribution': stats['difficulty_distribution']
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting game stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@leaderboard_bp.route('/stats/global', methods=['GET'])
def get_global_stats():
    """Get global leaderboard statistics"""
    try:
        stats = LeaderboardStats.get_global_stats()
        
        result = {
            'total_players': stats['total_players'],
            'active_games': stats['active_games'],
            'total_scores': stats['total_scores'],
            'global_average_score': float(stats['global_avg_score']) if stats['global_avg_score'] else 0
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting global stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@leaderboard_bp.route('/compare', methods=['POST'])
def compare_users():
    """Compare scores between multiple users"""
    try:
        data = request.get_json()
        
        if not data or 'user_ids' not in data or 'game_id' not in data:
            return jsonify({'error': 'Missing user_ids or game_id'}), 400
        
        user_ids = data['user_ids']
        game_id = data['game_id']
        time_period = data.get('time_period', 'all_time')
        
        if len(user_ids) > 10:  # Limit comparison to 10 users
            return jsonify({'error': 'Too many users for comparison (max 10)'}), 400
        
        # Validate time period
        valid_periods = ['daily', 'weekly', 'all_time']
        if time_period not in valid_periods:
            return jsonify({'error': 'Invalid time period'}), 400
        
        # Get ranks for all users
        comparison_data = []
        for user_id in user_ids:
            rank_info = LeaderboardScore.get_user_rank(user_id, game_id, time_period)
            if rank_info:
                comparison_data.append({
                    'user_id': user_id,
                    'rank_position': rank_info['rank_position'],
                    'score_value': float(rank_info['score_value']),
                    'achieved_at': rank_info['achieved_at'].isoformat() if rank_info['achieved_at'] else None
                })
        
        # Sort by rank
        comparison_data.sort(key=lambda x: x['rank_position'])
        
        result = {
            'game_id': game_id,
            'time_period': time_period,
            'total_compared': len(comparison_data),
            'comparison': comparison_data
        }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error comparing users: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@leaderboard_bp.route('/validate', methods=['POST'])
@login_required
def validate_score():
    """Validate a score without submitting it"""
    try:
        data = request.get_json()
        
        required_fields = ['game_id', 'score_value']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        game_id = int(data['game_id'])
        score_value = float(data['score_value'])
        playtime_seconds = data.get('playtime_seconds', 0)
        
        is_valid = LeaderboardScore.validate_score(game_id, score_value, playtime_seconds)
        
        return jsonify({
            'valid': is_valid,
            'message': 'Score is valid' if is_valid else 'Score validation failed'
        })
        
    except ValueError as e:
        return jsonify({'error': 'Invalid data format'}), 400
    except Exception as e:
        logger.error(f"Error validating score: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


# Error handlers
@leaderboard_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404


@leaderboard_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
