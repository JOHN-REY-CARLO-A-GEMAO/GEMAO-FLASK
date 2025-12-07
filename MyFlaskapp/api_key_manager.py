"""
API Key Management
"""

import secrets
import hashlib
from datetime import datetime
from MyFlaskapp.db import get_db_connection

def _hash_api_key(api_key: str) -> str:
    """Hashes an API key using SHA256."""
    return hashlib.sha256(api_key.encode()).hexdigest()

def create_api_key(user_id: int, permissions: str = None, expires_at: datetime = None) -> tuple[str, str]:
    """
    Creates a new API key for a user.
    Returns the raw API key and its hash.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    raw_api_key = secrets.token_urlsafe(32)
    key_hash = _hash_api_key(raw_api_key)
    try:
        cursor.execute(
            """
            INSERT INTO api_keys (key_hash, user_id, permissions, created_at, expires_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (key_hash, user_id, permissions, datetime.utcnow(), expires_at)
        )
        conn.commit()
        return raw_api_key, key_hash
    except Exception as e:
        conn.rollback()
        print(f"Error creating API key: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def get_api_key(key_hash: str):
    """Retrieves an API key by its hash."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM api_keys WHERE key_hash = %s", (key_hash,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error getting API key: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_user_api_keys(user_id: int):
    """Retrieves all API keys for a specific user."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM api_keys WHERE user_id = %s", (user_id,))
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting user API keys: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def update_api_key(key_id: int, permissions: str = None, expires_at: datetime = None) -> bool:
    """Updates an existing API key's permissions and expiration."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE api_keys SET permissions = %s, expires_at = %s WHERE id = %s
            """,
            (permissions, expires_at, key_id)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error updating API key: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def delete_api_key(key_id: int) -> bool:
    """Deletes an API key."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM api_keys WHERE id = %s", (key_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error deleting API key: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def validate_api_key(raw_api_key: str) -> dict | None:
    """
    Validates a raw API key and returns the key details if valid and active.
    """
    key_hash = _hash_api_key(raw_api_key)
    key_data = get_api_key(key_hash)
    if key_data and (key_data['expires_at'] is None or key_data['expires_at'] > datetime.utcnow()):
        return key_data
    return None
