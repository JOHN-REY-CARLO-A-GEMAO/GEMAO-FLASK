"""
Game Categories Management
"""

from MyFlaskapp.db import get_db_connection

def create_category(name: str, description: str) -> bool:
    """Creates a new game category."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO game_categories (name, description) VALUES (%s, %s)",
            (name, description)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error creating category: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_category(category_id: int):
    """Retrieves a single category by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM game_categories WHERE id = %s", (category_id,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error getting category: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_all_categories():
    """Retrieves all game categories."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM game_categories ORDER BY name")
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting all categories: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def update_category(category_id: int, name: str, description: str) -> bool:
    """Updates a game category."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE game_categories SET name = %s, description = %s WHERE id = %s",
            (name, description, category_id)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error updating category: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def delete_category(category_id: int) -> bool:
    """Deletes a game category."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM game_categories WHERE id = %s", (category_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error deleting category: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def add_game_to_category(game_id: int, category_id: int) -> bool:
    """Adds a game to a category."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO game_category_association (game_id, category_id) VALUES (%s, %s)",
            (game_id, category_id)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error adding game to category: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def remove_game_from_category(game_id: int, category_id: int) -> bool:
    """Removes a game from a category."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM game_category_association WHERE game_id = %s AND category_id = %s",
            (game_id, category_id)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error removing game from category: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_games_in_category(category_id: int):
    """Retrieves all games in a specific category."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT g.* FROM games g
            JOIN game_category_association gca ON g.id = gca.game_id
            WHERE gca.category_id = %s
            """,
            (category_id,)
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting games in category: {e}")
        return []
    finally:
        cursor.close()
        conn.close()
