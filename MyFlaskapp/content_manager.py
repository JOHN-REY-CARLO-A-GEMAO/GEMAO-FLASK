"""
Content Versioning Management
"""

from MyFlaskapp.db import get_db_connection

def create_content_version(content_id: int, content_type: str, content: str, author_id: int) -> bool:
    """Creates a new version for a piece of content."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Get the latest version number for this content
        cursor.execute(
            "SELECT MAX(version_number) FROM content_versions WHERE content_id = %s AND content_type = %s",
            (content_id, content_type)
        )
        latest_version = cursor.fetchone()[0]
        new_version_number = (latest_version or 0) + 1

        cursor.execute(
            """
            INSERT INTO content_versions (content_id, content_type, version_number, content, author_id)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (content_id, content_type, new_version_number, content, author_id)
        )
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error creating content version: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def get_content_versions(content_id: int, content_type: str):
    """Retrieves all versions for a given piece of content."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM content_versions WHERE content_id = %s AND content_type = %s ORDER BY version_number DESC",
            (content_id, content_type)
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"Error getting content versions: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_latest_content_version(content_id: int, content_type: str):
    """Retrieves the latest version of a piece of content."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM content_versions WHERE content_id = %s AND content_type = %s ORDER BY version_number DESC LIMIT 1",
            (content_id, content_type)
        )
        return cursor.fetchone()
    except Exception as e:
        print(f"Error getting latest content version: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def restore_content_version(version_id: int) -> bool:
    """
    Restores a specific content version, effectively making it the current active content.
    This implies updating the original content table (e.g., blog_posts).
    This function will require knowing the structure of the `blog_posts` table
    or a generic content table. For now, it will only mark the version as restored
    or retrieve the content of the version.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Get the content of the version to restore
        cursor.execute("SELECT content_id, content_type, content FROM content_versions WHERE id = %s", (version_id,))
        version_data = cursor.fetchone()

        if not version_data:
            return False

        content_id = version_data['content_id']
        content_type = version_data['content_type']
        content = version_data['content']

        if content_type == 'blog_post':
            # Update the actual blog_posts table with the content of the restored version
            cursor.execute(
                "UPDATE blog_posts SET content = %s WHERE id = %s",
                (content, content_id)
            )
            conn.commit()
            return True
        else:
            print(f"Unsupported content type for restoration: {content_type}")
            return False
    except Exception as e:
        conn.rollback()
        print(f"Error restoring content version: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
