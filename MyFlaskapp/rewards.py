"""
Rewards System - Points and Streaks
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

def update_streak(user_id: int, game_id: int) -> bool:
    """Updates the streak for a user and a game."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # For simplicity, we just increment the streak. A real implementation
        # would check the last_updated timestamp to see if the streak is current.
        cursor.execute(
            """
            INSERT INTO streaks (user_id, game_id, streak_count)
            VALUES (%s, %s, 1)
            ON DUPLICATE KEY UPDATE streak_count = streak_count + 1
            """,
            (user_id, game_id)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error updating streak: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_streak(user_id: int, game_id: int) -> int:
    """Retrieves the current streak for a user and a game."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT streak_count FROM streaks WHERE user_id = %s AND game_id = %s", (user_id, game_id))
        result = cursor.fetchone()
        return result[0] if result else 0
    except Exception as e:
        print(f"Error getting streak: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()
