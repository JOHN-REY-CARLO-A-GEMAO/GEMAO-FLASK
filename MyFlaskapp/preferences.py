"""
User Notification Preferences Management
"""

from MyFlaskapp.db import get_db_connection

def get_notification_preferences(user_id: int):
    """Retrieves a user's notification preferences."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM notification_preferences WHERE user_id = %s", (user_id,))
        prefs = cursor.fetchone()
        if not prefs:
            # If no preferences are set, return default values
            return {'user_id': user_id, 'email_notifications': True, 'sms_notifications': False}
        return prefs
    except Exception as e:
        print(f"Error getting notification preferences: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def update_notification_preferences(user_id: int, email_notifications: bool, sms_notifications: bool) -> bool:
    """Updates a user's notification preferences."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO notification_preferences (user_id, email_notifications, sms_notifications)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE email_notifications = %s, sms_notifications = %s
            """,
            (user_id, email_notifications, sms_notifications, email_notifications, sms_notifications)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error updating notification preferences: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
