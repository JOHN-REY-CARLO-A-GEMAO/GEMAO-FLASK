"""
Leaderboard Models and Database Operations
Comprehensive leaderboard system with score tracking, validation, and ranking
"""

import json
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from decimal import Decimal

from MyFlaskapp.db import get_db_connection
from MyFlaskapp.rewards import add_points, update_streak


class LeaderboardScore:
    """Model for individual leaderboard scores"""
    
    def __init__(self, score_data=None):
        if score_data:
            self.id = score_data.get('id')
            self.user_id = score_data.get('user_id')
            self.game_id = score_data.get('game_id')
            self.score_value = score_data.get('score_value')
            self.rank_position = score_data.get('rank_position')
            self.achieved_at = score_data.get('achieved_at')
            self.is_valid = score_data.get('is_valid', True)
            self.validation_hash = score_data.get('validation_hash')
            self.session_id = score_data.get('session_id')
            self.playtime_.seconds = score_data.get('playtime_seconds', 0)
            self.difficulty_level = score_data.get('difficulty_level', 'medium')
            self.additional_metrics = score_data.get('additional_metrics', {})
            self.created_at = score_data.get('created_at')
            self.updated_at = score_data.get('updated_at')
    
    @classmethod
    def create_score(cls, user_id: int, game_id: int, score_value: float, 
                    session_id: str = None, playtime_seconds: int = 0,
                    difficulty_level: str = 'medium', additional_metrics: Dict = None) -> 'LeaderboardScore':
        """Create a new score entry with validation"""
        
        # Generate validation hash
        validation_data = f"{user_id}{game_id}{score_value}{datetime.now()}"
        validation_hash = hashlib.sha256(validation_data.encode()).hexdigest()
        
        # Generate session ID if not provided
        if not session_id:
            session_id = secrets.token_urlsafe(16)
        
        score_data = {
            'user_id': user_id,
            'game_id': game_id,
            'score_value': score_value,
            'validation_hash': validation_hash,
            'session_id': session_id,
            'playtime_seconds': playtime_seconds,
            'difficulty_level': difficulty_level,
            'additional_metrics': json.dumps(additional_metrics) if additional_metrics else None
        }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Insert new score
            columns = ', '.join(score_data.keys())
            placeholders = ', '.join(['%s'] * len(score_data))
            query = f"INSERT INTO leaderboard_scores ({columns}) VALUES ({placeholders})"
            cursor.execute(query, list(score_data.values()))
            
            # Get the inserted score with generated rank
            cursor.execute(
                "SELECT * FROM leaderboard_scores WHERE id = %s",
                (cursor.lastrowid,)
            )
            result = cursor.fetchone()
            
            # Update user personal bests
            cls._update_personal_best(user_id, game_id, score_value)
            
            # Update ranking cache
            cls._update_ranking_cache(game_id, user_id, score_value)
            
            # Add points and update streak
            add_points(user_id, 10, "New score submitted")
            update_streak(user_id, game_id)
            
            conn.commit()
            return cls(result)
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @classmethod
    def _update_personal_best(cls, user_id: int, game_id: int, score_value: float):
        """Update user's personal best for a game"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Check if personal best exists
            cursor.execute(
                "SELECT best_score, total_plays, average_score FROM user_personal_bests WHERE user_id = %s AND game_id = %s",
                (user_id, game_id)
            )
            existing = cursor.fetchone()
            
            if existing:
                best_score, total_plays, average_score = existing
                
                # Calculate new average score
                new_average_score = ((average_score * total_plays) + score_value) / (total_plays + 1)

                if score_value > best_score:
                    # Update personal best and average score
                    cursor.execute("""
                        UPDATE user_personal_bests 
                        SET best_score = %s, achieved_at = NOW(), total_plays = total_plays + 1, average_score = %s
                        WHERE user_id = %s AND game_id = %s
                    """, (score_value, new_average_score, user_id, game_id))
                else:
                    # Just increment play count and update average score
                    cursor.execute("""
                        UPDATE user_personal_bests 
                        SET total_plays = total_plays + 1, last_played_at = NOW(), average_score = %s
                        WHERE user_id = %s AND game_id = %s
                    """, (new_average_score, user_id, game_id))
            else:
                # Create new personal best
                cursor.execute("""
                    INSERT INTO user_personal_bests (user_id, game_id, best_score, total_plays, average_score)
                    VALUES (%s, %s, %s, 1, %s)
                """, (user_id, game_id, score_value, score_value))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @classmethod
    def _update_ranking_cache(cls, game_id: int, user_id: int, score_value: float):
        """Update ranking cache for performance"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Update all-time ranking
            cursor.execute("""
                INSERT INTO leaderboard_rankings 
                (game_id, user_id, rank_position, score_value, achieved_at, time_period)
                VALUES (%s, %s, 
                    (SELECT COUNT(*) + 1 FROM leaderboard_scores ls2 
                     WHERE ls2.game_id = %s AND ls2.score_value > %s AND ls2.is_valid = TRUE),
                    %s, NOW(), 'all_time')
                ON DUPLICATE KEY UPDATE 
                rank_position = VALUES(rank_position),
                score_value = GREATEST(score_value, VALUES(score_value)),
                achieved_at = IF(score_value < VALUES(score_value), achieved_at, VALUES(achieved_at)),
                last_updated = NOW()
            """, (game_id, user_id, game_id, score_value, score_value))
            
            # Update daily ranking
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cursor.execute("""
                INSERT INTO leaderboard_rankings 
                (game_id, user_id, rank_position, score_value, achieved_at, time_period, period_start, period_end)
                VALUES (%s, %s, 
                    (SELECT COUNT(*) + 1 FROM leaderboard_scores ls2 
                     WHERE ls2.game_id = %s AND ls2.score_value > %s 
                     AND ls2.is_valid = TRUE AND ls2.achieved_at >= %s),
                    %s, NOW(), 'daily', %s, %s + INTERVAL 1 DAY)
                ON DUPLICATE KEY UPDATE 
                rank_position = VALUES(rank_position),
                score_value = GREATEST(score_value, VALUES(score_value)),
                achieved_at = IF(score_value < VALUES(score_value), achieved_at, VALUES(achieved_at)),
                last_updated = NOW()
            """, (game_id, user_id, game_id, score_value, today_start, score_value, today_start))
            
            # Update weekly ranking
            week_start = datetime.now() - timedelta(days=datetime.now().weekday())
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            cursor.execute("""
                INSERT INTO leaderboard_rankings 
                (game_id, user_id, rank_position, score_value, achieved_at, time_period, period_start, period_end)
                VALUES (%s, %s, 
                    (SELECT COUNT(*) + 1 FROM leaderboard_scores ls2 
                     WHERE ls2.game_id = %s AND ls2.score_value > %s 
                     AND ls2.is_valid = TRUE AND ls2.achieved_at >= %s),
                    %s, NOW(), 'weekly', %s, %s + INTERVAL 7 DAY)
                ON DUPLICATE KEY UPDATE 
                rank_position = VALUES(rank_position),
                score_value = GREATEST(score_value, VALUES(score_value)),
                achieved_at = IF(score_value < VALUES(score_value), achieved_at, VALUES(achieved_at)),
                last_updated = NOW()
            """, (game_id, user_id, game_id, score_value, week_start, score_value, week_start))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    @classmethod
    def get_top_scores(cls, game_id: int, limit: int = 10, 
                      time_period: str = 'all_time', difficulty: str = None) -> List['LeaderboardScore']:
        """Get top scores for a game"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            if time_period == 'all_time':
                # Get from main scores table
                query = """
                    SELECT ls.*, u.username, u.firstname, u.lastname
                    FROM leaderboard_scores ls
                    JOIN users u ON ls.user_id = u.id
                    WHERE ls.game_id = %s AND ls.is_valid = TRUE
                """
                params = [game_id]
                
                if difficulty:
                    query += " AND ls.difficulty_level = %s"
                    params.append(difficulty)
                
                query += " ORDER BY ls.score_value DESC, ls.achieved_at ASC LIMIT %s"
                params.append(limit)
                
            else:
                # Get from ranking cache
                time_filter = cls._get_time_filter(time_period)
                query = """
                    SELECT lr.*, u.username, u.firstname, u.lastname
                    FROM leaderboard_rankings lr
                    JOIN users u ON lr.user_id = u.id
                    WHERE lr.game_id = %s AND lr.time_period = %s
                """
                params = [game_id, time_period]
                
                if difficulty:
                    query += """
                        AND lr.user_id IN (
                            SELECT DISTINCT user_id FROM leaderboard_scores 
                            WHERE game_id = %s AND difficulty_level = %s
                        )
                    """
                    params.extend([game_id, difficulty])
                
                query += " ORDER BY lr.rank_position ASC LIMIT %s"
                params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            return [cls(result) for result in results]
            
        finally:
            cursor.close()
            conn.close()
    
    @classmethod
    def _get_time_filter(cls, time_period: str) -> str:
        """Get time filter for queries"""
        if time_period == 'daily':
            return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_period == 'weekly':
            week_start = datetime.now() - timedelta(days=datetime.now().weekday())
            return week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        return None
    
    @classmethod
    def get_user_rank(cls, user_id: int, game_id: int, time_period: str = 'all_time') -> Optional[Dict]:
        """Get user's rank for a specific game"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            if time_period == 'all_time':
                cursor.execute("""
                    SELECT ls.rank_position, ls.score_value, ls.achieved_at,
                           (SELECT COUNT(*) FROM leaderboard_scores ls2 
                            WHERE ls2.game_id = %s AND ls2.is_valid = TRUE) as total_players
                    FROM leaderboard_scores ls
                    WHERE ls.user_id = %s AND ls.game_id = %s AND ls.is_valid = TRUE
                    ORDER BY ls.score_value DESC
                    LIMIT 1
                """, (game_id, user_id, game_id))
            else:
                cursor.execute("""
                    SELECT lr.rank_position, lr.score_value, lr.achieved_at,
                           (SELECT COUNT(*) FROM leaderboard_rankings lr2 
                            WHERE lr2.game_id = %s AND lr2.time_period = %s) as total_players
                    FROM leaderboard_rankings lr
                    WHERE lr.user_id = %s AND lr.game_id = %s AND lr.time_period = %s
                """, (game_id, user_id, game_id, time_period))
            
            result = cursor.fetchone()
            return result
            
        finally:
            cursor.close()
            conn.close()
    
    @classmethod
    def validate_score(cls, game_id: int, score_value: float, playtime_seconds: int) -> bool:
        """Validate score against game rules"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT max_score, min_score, max_playtime_seconds, validation_rules
                FROM score_validation_rules
                WHERE game_id = %s AND is_active = TRUE
            """, (game_id,))
            
            rules = cursor.fetchone()
            if not rules:
                return True  # No rules defined, accept score
            
            # Basic validation
            if score_value < rules['min_score'] or score_value > rules['max_score']:
                return False
            
            if rules['max_playtime_seconds'] and playtime_seconds > rules['max_playtime_seconds']:
                return False
            
            # Advanced validation rules
            if rules['validation_rules']:
                validation_rules = json.loads(rules['validation_rules'])
                
                # Check score per minute
                if 'max_score_per_minute' in validation_rules and playtime_seconds > 0:
                    score_per_minute = (score_value / playtime_seconds) * 60
                    if score_per_minute > validation_rules['max_score_per_minute']:
                        return False
            
            return True
            
        finally:
            cursor.close()
            conn.close()
    
    @classmethod
    def get_user_scores(cls, user_id: int, game_id: int = None, limit: int = 50) -> List['LeaderboardScore']:
        """Get scores for a specific user"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            query = """
                SELECT ls.*, g.name as game_name
                FROM leaderboard_scores ls
                JOIN games g ON ls.game_id = g.id
                WHERE ls.user_id = %s AND ls.is_valid = TRUE
            """
            params = [user_id]
            
            if game_id:
                query += " AND ls.game_id = %s"
                params.append(game_id)
            
            query += " ORDER BY ls.score_value DESC, ls.achieved_at DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            return [cls(result) for result in results]
            
        finally:
            cursor.close()
            conn.close()
    
    @classmethod
    def get_personal_bests(cls, user_id: int) -> List[Dict]:
        """Get user's personal best scores across all games"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT upb.*, g.name as game_name, g.description
                FROM user_personal_bests upb
                JOIN games g ON upb.game_id = g.id
                WHERE upb.user_id = %s
                ORDER BY upb.best_score DESC
            """, (user_id,))
            
            return cursor.fetchall()
            
        finally:
            cursor.close()
            conn.close()


class LeaderboardStats:
    """Statistics and analytics for leaderboards"""
    
    @classmethod
    def get_game_stats(cls, game_id: int) -> Dict:
        """Get comprehensive statistics for a game"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Basic stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_plays,
                    COUNT(DISTINCT user_id) as unique_players,
                    AVG(score_value) as avg_score,
                    MAX(score_value) as high_score,
                    MIN(score_value) as low_score
                FROM leaderboard_scores
                WHERE game_id = %s AND is_valid = TRUE
            """, (game_id,))
            
            basic_stats = cursor.fetchone()
            
            # Recent activity
            cursor.execute("""
                SELECT COUNT(*) as plays_today
                FROM leaderboard_scores
                WHERE game_id = %s AND is_valid = TRUE 
                AND DATE(achieved_at) = CURDATE()
            """, (game_id,))
            
            recent_stats = cursor.fetchone()
            
            # Difficulty distribution
            cursor.execute("""
                SELECT difficulty_level, COUNT(*) as count
                FROM leaderboard_scores
                WHERE game_id = %s AND is_valid = TRUE
                GROUP BY difficulty_level
            """, (game_id,))
            
            difficulty_stats = cursor.fetchall()
            
            return {
                **basic_stats,
                **recent_stats,
                'difficulty_distribution': {d['difficulty_level']: d['count'] for d in difficulty_stats}
            }
            
        finally:
            cursor.close()
            conn.close()
    
    @classmethod
    def get_global_stats(cls) -> Dict:
        """Get global leaderboard statistics"""
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT ls.user_id) as total_players,
                    COUNT(DISTINCT ls.game_id) as active_games,
                    COUNT(*) as total_scores,
                    AVG(ls.score_value) as global_avg_score
                FROM leaderboard_scores ls
                WHERE ls.is_valid = TRUE
            """)
            
            return cursor.fetchone()
            
        finally:
            cursor.close()
            conn.close()
