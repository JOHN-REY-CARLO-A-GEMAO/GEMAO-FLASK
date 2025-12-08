#!/usr/bin/env python3
"""
Populate leaderboard data separately to avoid SELECT statement conflicts
"""

import mysql.connector
from mysql.connector import Error
import sys
import random
from datetime import datetime, timedelta

def create_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='gemao_db',
            autocommit=False
        )
        print("Successfully connected to gemao_db database")
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def get_user_ids(connection):
    """Get all user IDs from database"""
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE role = 'user'")
        return [row[0] for row in cursor.fetchall()]
    finally:
        cursor.close()

def get_game_ids(connection):
    """Get all game IDs from database"""
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT id FROM games")
        return [row[0] for row in cursor.fetchall()]
    finally:
        cursor.close()

def populate_leaderboard_scores(connection, user_ids, game_ids):
    """Populate leaderboard scores with sample data"""
    cursor = connection.cursor()
    
    # Sample score data
    sample_scores = [
        (98500.00, 1800, 'hard', '{"kills": 45, "deaths": 3, "accuracy": 89.5}'),
        (94200.00, 1650, 'hard', '{"kills": 42, "deaths": 5, "accuracy": 87.2}'),
        (87800.00, 1920, 'medium', '{"kills": 38, "deaths": 7, "accuracy": 82.1}'),
        (96500.00, 1740, 'hard', '{"kills": 44, "deaths": 4, "accuracy": 88.9}'),
        (82300.00, 2100, 'medium', '{"kills": 35, "deaths": 9, "accuracy": 79.3}'),
        (89200.00, 2400, 'expert', '{"questions_correct": 28, "time_bonus": 1500, "hints_used": 2}'),
        (93400.00, 2250, 'expert', '{"questions_correct": 30, "time_bonus": 1800, "hints_used": 1}'),
        (87600.00, 2580, 'hard', '{"questions_correct": 27, "time_bonus": 1200, "hints_used": 3}'),
        (91800.00, 2340, 'expert', '{"questions_correct": 29, "time_bonus": 1650, "hints_used": 2}'),
        (84500.00, 2720, 'hard', '{"questions_correct": 25, "time_bonus": 1000, "hints_used": 4}'),
        (96800.00, 1500, 'hard', '{"rasengan_power": 95, "control_score": 92, "attempts": 15}'),
        (98200.00, 1380, 'hard', '{"rasengan_power": 98, "control_score": 96, "attempts": 12}'),
        (94500.00, 1620, 'hard', '{"rasengan_power": 93, "control_score": 90, "attempts": 18}'),
        (89700.00, 1860, 'medium', '{"rasengan_power": 87, "control_score": 85, "attempts": 22}'),
        (92300.00, 1710, 'hard', '{"rasengan_power": 91, "control_score": 88, "attempts": 16}'),
        (95600.00, 1950, 'expert', '{"sharingan_activated": true, "victories": 12, "defeats": 2}'),
        (93400.00, 2100, 'expert', '{"sharingan_activated": true, "victories": 11, "defeats": 3}'),
        (87900.00, 2280, 'hard', '{"sharingan_activated": false, "victories": 9, "defeats": 5}'),
        (97100.00, 1830, 'expert', '{"sharingan_activated": true, "victories": 13, "defeats": 1}'),
        (89800.00, 2160, 'hard', '{"sharingan_activated": false, "victories": 10, "defeats": 4}'),
        (99200.00, 2700, 'expert', '{"waves_survived": 15, "enemies_defeated": 287, "buildings_saved": 8}'),
        (97800.00, 2850, 'expert', '{"waves_survived": 14, "enemies_defeated": 265, "buildings_saved": 7}'),
        (92400.00, 3000, 'hard', '{"waves_survived": 12, "enemies_defeated": 234, "buildings_saved": 6}'),
        (95600.00, 2760, 'expert', '{"waves_survived": 13, "enemies_defeated": 251, "buildings_saved": 7}'),
        (88900.00, 3120, 'hard', '{"waves_survived": 11, "enemies_defeated": 198, "buildings_saved": 5}'),
    ]
    
    try:
        # Insert sample scores
        for i, (user_id, game_id) in enumerate([(uid, gid) for uid in user_ids[:10] for gid in game_ids[:5]]):
            if i < len(sample_scores):
                score_data = sample_scores[i]
                score_value = score_data[0]
                playtime_seconds = score_data[1]
                difficulty_level = score_data[2]
                additional_metrics = score_data[3]
                
                # Generate random achieved_at date within last 30 days
                days_ago = random.randint(1, 30)
                achieved_at = datetime.now() - timedelta(days=days_ago)
                
                query = """
                    INSERT INTO leaderboard_scores 
                    (user_id, game_id, score_value, achieved_at, is_valid, session_id, playtime_seconds, difficulty_level, additional_metrics)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                cursor.execute(query, (
                    user_id, game_id, score_value, achieved_at, True,
                    f'sess_{i+1:03d}', playtime_seconds, difficulty_level, additional_metrics
                ))
        
        connection.commit()
        print(f"Inserted {cursor.rowcount} leaderboard scores")
        
    except Error as e:
        print(f"Error populating leaderboard scores: {e}")
        connection.rollback()
    finally:
        cursor.close()

def populate_personal_bests(connection):
    """Update user personal bests based on scores"""
    cursor = connection.cursor()
    
    try:
        # Calculate and insert personal bests
        query = """
            INSERT INTO user_personal_bests (user_id, game_id, best_score, best_rank, achieved_at, total_plays, average_score, last_played_at)
            SELECT 
                user_id, 
                game_id, 
                MAX(score_value) as best_score,
                1 as best_rank,
                MAX(achieved_at) as achieved_at,
                COUNT(*) as total_plays,
                AVG(score_value) as average_score,
                MAX(achieved_at) as last_played_at
            FROM leaderboard_scores 
            GROUP BY user_id, game_id
            ON DUPLICATE KEY UPDATE
                best_score = VALUES(best_score),
                best_rank = VALUES(best_rank),
                achieved_at = VALUES(achieved_at),
                total_plays = VALUES(total_plays),
                average_score = VALUES(average_score),
                last_played_at = VALUES(last_played_at)
        """
        
        cursor.execute(query)
        connection.commit()
        print(f"Updated {cursor.rowcount} personal best records")
        
    except Error as e:
        print(f"Error updating personal bests: {e}")
        connection.rollback()
    finally:
        cursor.close()

def populate_rankings(connection):
    """Update leaderboard rankings cache"""
    cursor = connection.cursor()
    
    try:
        # Clear existing rankings
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
        connection.commit()
        print(f"Updated {cursor.rowcount} ranking records")
        
    except Error as e:
        print(f"Error updating rankings: {e}")
        connection.rollback()
    finally:
        cursor.close()

def main():
    """Main function to populate leaderboard data"""
    print("Populating leaderboard data...")
    
    connection = create_connection()
    if not connection:
        sys.exit(1)
    
    try:
        # Get existing data
        user_ids = get_user_ids(connection)
        game_ids = get_game_ids(connection)
        
        print(f"Found {len(user_ids)} users and {len(game_ids)} games")
        
        # Populate data
        populate_leaderboard_scores(connection, user_ids, game_ids)
        populate_personal_bests(connection)
        populate_rankings(connection)
        
        # Show statistics
        cursor = connection.cursor()
        try:
            tables = ['leaderboard_scores', 'user_personal_bests', 'leaderboard_rankings']
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table}: {count} records")
        finally:
            cursor.close()
            
        print("Leaderboard data population completed successfully!")
        
    except Exception as e:
        print(f"Error during population: {e}")
        sys.exit(1)
    finally:
        if connection.is_connected():
            connection.close()
            print("Database connection closed")

if __name__ == "__main__":
    main()
