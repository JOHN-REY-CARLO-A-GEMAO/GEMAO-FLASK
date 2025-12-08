"""
Rewards System - Points
"""

from MyFlaskapp.db import get_db_connection

def add_points(user_id: int, points: int, reason: str) -> bool:
    """Adds points to a user and creates a transaction."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Update user_points table
        cursor.execute(
            """
            INSERT INTO user_points (user_id, points)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE points = points + %s
            """,
            (user_id, points, points)
        )
        # Create a transaction
        cursor.execute(
            """
            INSERT INTO points_transactions (user_id, points, reason)
            VALUES (%s, %s, %s)
            """,
            (user_id, points, reason)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error adding points: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_points(user_id: int) -> int:
    """Retrieves the current points for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT points FROM user_points WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 0
    except Exception as e:
        print(f"Error getting points: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()

# Streak functions removed - streaks table has been dropped
# def update_streak(user_id: int, game_id: int) -> bool:
# def get_streak(user_id: int, game_id: int) -> int:
