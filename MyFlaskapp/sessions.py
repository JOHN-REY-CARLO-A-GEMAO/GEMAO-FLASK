"""
User Sessions Management
"""

import secrets
from datetime import datetime, timedelta
from MyFlaskapp.db import get_db_connection

def create_session(user_id: int, ip_address: str, user_agent: str) -> str:
    """Creates a new user session."""
    conn = get_db_connection()
    cursor = conn.cursor()
    session_token = secrets.token_hex(32)
    expires_at = datetime.utcnow() + timedelta(days=30)
    try:
        cursor.execute(
            """
            INSERT INTO user_sessions (user_id, session_token, ip_address, user_agent, expires_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (user_id, session_token, ip_address, user_agent, expires_at)
        )
        conn.commit()
        return session_token
    except Exception as e:
        conn.rollback()
        print(f"Error creating session: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def get_session(session_token: str):
    """Retrieves a session by its token."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM user_sessions WHERE session_token = %s", (session_token,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error getting session: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def delete_session(session_token: str) -> bool:
    """Deletes a session."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM user_sessions WHERE session_token = %s", (session_token,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error deleting session: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
