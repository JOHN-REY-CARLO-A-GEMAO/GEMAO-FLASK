"""
Leaderboard Backup and Recovery System
Provides comprehensive backup and recovery procedures for leaderboard data
"""

import json
import csv
import os
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from MyFlaskapp.db import get_db_connection

logger = logging.getLogger(__name__)


class LeaderboardBackup:
    """Handles backup and recovery of leaderboard data"""
    
    def __init__(self, backup_dir: str = "backups/leaderboard"):
        self.backup_dir = backup_dir
        self.ensure_backup_dir()
    
    def ensure_backup_dir(self):
        """Create backup directory if it doesn't exist"""
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(os.path.join(self.backup_dir, "daily"), exist_ok=True)
        os.makedirs(os.path.join(self.backup_dir, "weekly"), exist_ok=True)
        os.makedirs(os.path.join(self.backup_dir, "monthly"), exist_ok=True)
    
    def create_backup(self, backup_type: str = "full") -> Dict:
        """Create a backup of leaderboard data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.backup_dir, f"leaderboard_backup_{timestamp}.json")
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            backup_data = {
                "backup_info": {
                    "timestamp": timestamp,
                    "type": backup_type,
                    "created_at": datetime.now().isoformat()
                },
                "scores": [],
                "personal_bests": [],
                "validation_rules": [],
                "rankings_cache": []
            }
            
            if backup_type in ["full", "scores"]:
                # Backup leaderboard scores
                cursor.execute("SELECT * FROM leaderboard_scores")
                backup_data["scores"] = self._serialize_results(cursor.fetchall())
            
            if backup_type in ["full", "personal_bests"]:
                # Backup personal bests
                cursor.execute("SELECT * FROM user_personal_bests")
                backup_data["personal_bests"] = self._serialize_results(cursor.fetchall())
            
            if backup_type in ["full", "validation_rules"]:
                # Backup validation rules
                cursor.execute("SELECT * FROM score_validation_rules")
                backup_data["validation_rules"] = self._serialize_results(cursor.fetchall())
            
            if backup_type in ["full", "rankings"]:
                # Backup rankings cache
                cursor.execute("SELECT * FROM leaderboard_rankings")
                backup_data["rankings_cache"] = self._serialize_results(cursor.fetchall())
            
            cursor.close()
            conn.close()
            
            # Write backup to file
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2, default=str)
            
            logger.info(f"Created {backup_type} backup: {backup_file}")
            
            return {
                "success": True,
                "backup_file": backup_file,
                "timestamp": timestamp,
                "type": backup_type,
                "size": os.path.getsize(backup_file),
                "records": {
                    "scores": len(backup_data["scores"]),
                    "personal_bests": len(backup_data["personal_bests"]),
                    "validation_rules": len(backup_data["validation_rules"]),
                    "rankings_cache": len(backup_data["rankings_cache"])
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to create backup: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def restore_backup(self, backup_file: str, restore_type: str = "full") -> Dict:
        """Restore leaderboard data from backup"""
        try:
            if not os.path.exists(backup_file):
                return {"success": False, "error": "Backup file not found"}
            
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            restored_records = {}
            
            if restore_type in ["full", "scores"] and "scores" in backup_data:
                # Clear existing scores if full restore
                if restore_type == "full":
                    cursor.execute("DELETE FROM leaderboard_scores")
                
                # Restore scores
                scores = backup_data["scores"]
                for score in scores:
                    # Convert datetime strings back to datetime objects
                    if 'achieved_at' in score and score['achieved_at']:
                        score['achieved_at'] = datetime.fromisoformat(score['achieved_at'])
                    if 'created_at' in score and score['created_at']:
                        score['created_at'] = datetime.fromisoformat(score['created_at'])
                    if 'updated_at' in score and score['updated_at']:
                        score['updated_at'] = datetime.fromisoformat(score['updated_at'])
                    
                    # Insert score
                    columns = list(score.keys())
                    placeholders = ', '.join(['%s'] * len(columns))
                    query = f"INSERT INTO leaderboard_scores ({', '.join(columns)}) VALUES ({placeholders})"
                    cursor.execute(query, list(score.values()))
                
                restored_records["scores"] = len(scores)
            
            if restore_type in ["full", "personal_bests"] and "personal_bests" in backup_data:
                # Clear existing personal bests if full restore
                if restore_type == "full":
                    cursor.execute("DELETE FROM user_personal_bests")
                
                # Restore personal bests
                bests = backup_data["personal_bests"]
                for best in bests:
                    # Convert datetime strings
                    if 'achieved_at' in best and best['achieved_at']:
                        best['achieved_at'] = datetime.fromisoformat(best['achieved_at'])
                    if 'last_played_at' in best and best['last_played_at']:
                        best['last_played_at'] = datetime.fromisoformat(best['last_played_at'])
                    
                    columns = list(best.keys())
                    placeholders = ', '.join(['%s'] * len(columns))
                    query = f"INSERT INTO user_personal_bests ({', '.join(columns)}) VALUES ({placeholders})"
                    cursor.execute(query, list(best.values()))
                
                restored_records["personal_bests"] = len(bests)
            
            if restore_type in ["full", "validation_rules"] and "validation_rules" in backup_data:
                # Clear existing rules if full restore
                if restore_type == "full":
                    cursor.execute("DELETE FROM score_validation_rules")
                
                # Restore validation rules
                rules = backup_data["validation_rules"]
                for rule in rules:
                    if 'created_at' in rule and rule['created_at']:
                        rule['created_at'] = datetime.fromisoformat(rule['created_at'])
                    
                    columns = list(rule.keys())
                    placeholders = ', '.join(['%s'] * len(columns))
                    query = f"INSERT INTO score_validation_rules ({', '.join(columns)}) VALUES ({placeholders})"
                    cursor.execute(query, list(rule.values()))
                
                restored_records["validation_rules"] = len(rules)
            
            if restore_type in ["full", "rankings"] and "rankings_cache" in backup_data:
                # Clear existing cache if full restore
                if restore_type == "full":
                    cursor.execute("DELETE FROM leaderboard_rankings")
                
                # Restore rankings cache
                rankings = backup_data["rankings_cache"]
                for ranking in rankings:
                    if 'achieved_at' in ranking and ranking['achieved_at']:
                        ranking['achieved_at'] = datetime.fromisoformat(ranking['achieved_at'])
                    if 'period_start' in ranking and ranking['period_start']:
                        ranking['period_start'] = datetime.fromisoformat(ranking['period_start'])
                    if 'period_end' in ranking and ranking['period_end']:
                        ranking['period_end'] = datetime.fromisoformat(ranking['period_end'])
                    if 'last_updated' in ranking and ranking['last_updated']:
                        ranking['last_updated'] = datetime.fromisoformat(ranking['last_updated'])
                    
                    columns = list(ranking.keys())
                    placeholders = ', '.join(['%s'] * len(columns))
                    query = f"INSERT INTO leaderboard_rankings ({', '.join(columns)}) VALUES ({placeholders})"
                    cursor.execute(query, list(ranking.values()))
                
                restored_records["rankings_cache"] = len(rankings)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Restored {restore_type} backup from: {backup_file}")
            
            return {
                "success": True,
                "backup_file": backup_file,
                "restore_type": restore_type,
                "restored_records": restored_records
            }
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {str(e)}")
            if 'conn' in locals():
                conn.rollback()
                if 'cursor' in locals():
                    cursor.close()
                conn.close()
            return {
                "success": False,
                "error": str(e)
            }
    
    def export_to_csv(self, table_name: str, output_file: str = None) -> Dict:
        """Export leaderboard data to CSV format"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.backup_dir, f"{table_name}_export_{timestamp}.csv")
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Get table data
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            if not rows:
                cursor.close()
                conn.close()
                return {"success": False, "error": f"No data found in table {table_name}"}
            
            # Write to CSV
            with open(output_file, 'w', newline='') as csvfile:
                fieldnames = rows[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            
            cursor.close()
            conn.close()
            
            logger.info(f"Exported {len(rows)} records from {table_name} to {output_file}")
            
            return {
                "success": True,
                "output_file": output_file,
                "table": table_name,
                "records": len(rows),
                "size": os.path.getsize(output_file)
            }
            
        except Exception as e:
            logger.error(f"Failed to export {table_name}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def list_backups(self) -> List[Dict]:
        """List all available backup files"""
        backups = []
        
        try:
            for filename in os.listdir(self.backup_dir):
                if filename.endswith('.json') and 'backup' in filename:
                    filepath = os.path.join(self.backup_dir, filename)
                    stat = os.stat(filepath)
                    
                    try:
                        with open(filepath, 'r') as f:
                            backup_data = json.load(f)
                            backup_info = backup_data.get('backup_info', {})
                        
                        backups.append({
                            "filename": filename,
                            "filepath": filepath,
                            "size": stat.st_size,
                            "created": datetime.fromtimestamp(stat.st_ctime),
                            "modified": datetime.fromtimestamp(stat.st_mtime),
                            "type": backup_info.get('type', 'unknown'),
                            "timestamp": backup_info.get('timestamp', 'unknown')
                        })
                    except:
                        # Skip corrupted backup files
                        continue
            
            # Sort by creation date (newest first)
            backups.sort(key=lambda x: x['created'], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list backups: {str(e)}")
        
        return backups
    
    def cleanup_old_backups(self, days_to_keep: int = 30) -> Dict:
        """Remove old backup files"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        removed_files = []
        
        try:
            for filename in os.listdir(self.backup_dir):
                filepath = os.path.join(self.backup_dir, filename)
                if os.path.isfile(filepath):
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_time < cutoff_date:
                        os.remove(filepath)
                        removed_files.append(filename)
            
            logger.info(f"Cleaned up {len(removed_files)} old backup files")
            
            return {
                "success": True,
                "removed_files": removed_files,
                "count": len(removed_files),
                "cutoff_date": cutoff_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _serialize_results(self, results: List[Dict]) -> List[Dict]:
        """Serialize database results for JSON storage"""
        serialized = []
        
        for result in results:
            serialized_item = {}
            for key, value in result.items():
                if isinstance(value, datetime):
                    serialized_item[key] = value.isoformat()
                else:
                    serialized_item[key] = value
            serialized.append(serialized_item)
        
        return serialized
    
    def get_backup_stats(self) -> Dict:
        """Get statistics about backups"""
        try:
            backups = self.list_backups()
            
            total_size = sum(b['size'] for b in backups)
            backup_types = {}
            
            for backup in backups:
                backup_type = backup['type']
                backup_types[backup_type] = backup_types.get(backup_type, 0) + 1
            
            return {
                "total_backups": len(backups),
                "total_size": total_size,
                "backup_types": backup_types,
                "latest_backup": backups[0] if backups else None,
                "oldest_backup": backups[-1] if backups else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get backup stats: {str(e)}")
            return {"error": str(e)}


class LeaderboardMaintenance:
    """Maintenance tasks for leaderboard system"""
    
    @staticmethod
    def rebuild_rankings_cache(game_id: int = None) -> Dict:
        """Rebuild the rankings cache for performance"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if game_id:
                # Rebuild for specific game
                cursor.execute("DELETE FROM leaderboard_rankings WHERE game_id = %s", (game_id,))
                
                # Rebuild all-time rankings
                cursor.execute("""
                    INSERT INTO leaderboard_rankings (game_id, user_id, rank_position, score_value, achieved_at, time_period)
                    SELECT 
                        game_id, user_id, 
                        DENSE_RANK() OVER (PARTITION BY game_id ORDER BY score_value DESC),
                        score_value, achieved_at, 'all_time'
                    FROM leaderboard_scores 
                    WHERE game_id = %s AND is_valid = TRUE
                """, (game_id,))
                
                affected_games = [game_id]
            else:
                # Rebuild for all games
                cursor.execute("DELETE FROM leaderboard_rankings")
                
                # Rebuild all-time rankings for all games
                cursor.execute("""
                    INSERT INTO leaderboard_rankings (game_id, user_id, rank_position, score_value, achieved_at, time_period)
                    SELECT 
                        game_id, user_id, 
                        DENSE_RANK() OVER (PARTITION BY game_id ORDER BY score_value DESC),
                        score_value, achieved_at, 'all_time'
                    FROM leaderboard_scores 
                    WHERE is_valid = TRUE
                """)
                
                cursor.execute("SELECT DISTINCT game_id FROM games")
                affected_games = [row[0] for row in cursor.fetchall()]
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Rebuilt rankings cache for games: {affected_games}")
            
            return {
                "success": True,
                "affected_games": affected_games,
                "games_count": len(affected_games)
            }
            
        except Exception as e:
            logger.error(f"Failed to rebuild rankings cache: {str(e)}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def invalidate_suspicious_scores(user_id: int = None, game_id: int = None) -> Dict:
        """Invalidate suspicious scores based on validation rules"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Find suspicious scores
            query = """
                SELECT ls.*, svr.validation_rules
                FROM leaderboard_scores ls
                LEFT JOIN score_validation_rules svr ON ls.game_id = svr.game_id
                WHERE ls.is_valid = TRUE
            """
            params = []
            
            if user_id:
                query += " AND ls.user_id = %s"
                params.append(user_id)
            
            if game_id:
                query += " AND ls.game_id = %s"
                params.append(game_id)
            
            cursor.execute(query, params)
            scores = cursor.fetchall()
            
            invalidated_scores = []
            
            for score in scores:
                if score['validation_rules']:
                    validation_rules = json.loads(score['validation_rules'])
                    
                    # Check for suspicious patterns
                    is_suspicious = False
                    
                    # Check score per minute
                    if 'max_score_per_minute' in validation_rules and score['playtime_seconds'] > 0:
                        score_per_minute = (score['score_value'] / score['playtime_seconds']) * 60
                        if score_per_minute > validation_rules['max_score_per_minute']:
                            is_suspicious = True
                    
                    # Check for impossible scores
                    if 'impossible_threshold' in validation_rules:
                        if score['score_value'] > validation_rules['impossible_threshold']:
                            is_suspicious = True
                    
                    if is_suspicious:
                        # Invalidate the score
                        cursor.execute(
                            "UPDATE leaderboard_scores SET is_valid = FALSE WHERE id = %s",
                            (score['id'],)
                        )
                        invalidated_scores.append(score['id'])
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Invalidated {len(invalidated_scores)} suspicious scores")
            
            return {
                "success": True,
                "invalidated_scores": invalidated_scores,
                "count": len(invalidated_scores)
            }
            
        except Exception as e:
            logger.error(f"Failed to invalidate suspicious scores: {str(e)}")
            return {"success": False, "error": str(e)}


# Scheduled tasks (can be integrated with cron or task scheduler)
def scheduled_backup():
    """Create scheduled daily backup"""
    backup = LeaderboardBackup()
    result = backup.create_backup("full")
    
    if result["success"]:
        # Clean up old backups (keep 30 days)
        backup.cleanup_old_backups(30)
    
    return result


def scheduled_maintenance():
    """Perform scheduled maintenance tasks"""
    # Rebuild rankings cache
    maintenance = LeaderboardMaintenance()
    cache_result = maintenance.rebuild_rankings_cache()
    
    # Invalidate suspicious scores
    invalidation_result = maintenance.invalidate_suspicious_scores()
    
    return {
        "cache_rebuild": cache_result,
        "score_invalidation": invalidation_result
    }
