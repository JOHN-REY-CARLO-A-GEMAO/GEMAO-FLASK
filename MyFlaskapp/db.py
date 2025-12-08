import os
import mysql.connector
from mysql.connector import Error
from .config import Config

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB  # Specify the database here
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_db_commands():
    """Initializes the database and tables."""
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB}")
        cursor.execute(f"USE {Config.MYSQL_DB}")

        # 1. Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                firstname VARCHAR(100) NOT NULL,
                middlename VARCHAR(100) NULL,
                lastname VARCHAR(100) NOT NULL,
                birthday DATE NULL,
                age INT NULL,
                contact_number VARCHAR(20) NULL,
                role ENUM('User', 'Admin') NOT NULL DEFAULT 'User',
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Profiles table removed; single-table user schema now contains optional fields

        # 3. OTP Verification Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS otp_verification (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                otp_code VARCHAR(6),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # 4. Games Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                file_path VARCHAR(255),
                image_path VARCHAR(255)
            )
        """)

        # 5. Game Access (Many-to-Many: Users <-> Games)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_access (
                user_id INT,
                game_id INT,
                is_allowed BOOLEAN DEFAULT FALSE,
                PRIMARY KEY (user_id, game_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
            )
        """)

        # 6. Audit Logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                actor_id INT,
                target_user_id INT,
                action VARCHAR(100),
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (actor_id) REFERENCES users(id) ON DELETE SET NULL,
                FOREIGN KEY (target_user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)

        # 7. Blog Posts Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blog_posts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                author_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)

        # 8. Streaks Table - REMOVED (unused)
        # Streaks table has been dropped as it's not implemented in frontend

        # 9. User Points Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_points (
                user_id INT PRIMARY KEY,
                points INT NOT NULL DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # 10. Points Transactions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS points_transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                points INT NOT NULL,
                reason VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # 11. Game Categories Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT
            )
        """)

        # 12. Game Category Association Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_category_association (
                game_id INT,
                category_id INT,
                PRIMARY KEY (game_id, category_id),
                FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES game_categories(id) ON DELETE CASCADE
            )
        """)

        # 13. User Sessions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                session_token VARCHAR(255) NOT NULL UNIQUE,
                ip_address VARCHAR(45),
                user_agent VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # 14. Notification Preferences Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notification_preferences (
                user_id INT PRIMARY KEY,
                email_notifications BOOLEAN DEFAULT TRUE,
                sms_notifications BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        
        # 16. Content Versions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_versions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                content_id INT NOT NULL,
                content_type VARCHAR(50) NOT NULL, -- e.g., 'blog_post'
                version_number INT NOT NULL,
                content TEXT NOT NULL,
                author_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)
        
        # Migration: bring existing installations to single-table user schema
        try:
            # Add missing columns on users
            cursor.execute(f"""
                SELECT COLUMN_NAME FROM information_schema.columns
                WHERE table_schema = '{Config.MYSQL_DB}' AND table_name = 'users'
            """)
            existing_cols = {row[0] for row in cursor.fetchall()}
            add_cols = []
            if 'middlename' not in existing_cols:
                add_cols.append("ADD COLUMN middlename VARCHAR(100) NULL")
            if 'birthday' not in existing_cols:
                add_cols.append("ADD COLUMN birthday DATE NULL")
            if 'age' not in existing_cols:
                add_cols.append("ADD COLUMN age INT NULL")
            if 'contact_number' not in existing_cols:
                add_cols.append("ADD COLUMN contact_number VARCHAR(20) NULL")
            if 'profile_picture_path' not in existing_cols:
                add_cols.append("ADD COLUMN profile_picture_path VARCHAR(255) NULL")
            if 'profile_picture_updated_at' not in existing_cols:
                add_cols.append("ADD COLUMN profile_picture_updated_at TIMESTAMP NULL")
            if add_cols:
                cursor.execute(f"ALTER TABLE users {', '.join(add_cols)}")

            # Normalize role casing before changing enum
            cursor.execute("UPDATE users SET role='Admin' WHERE role='admin'")
            cursor.execute("UPDATE users SET role='User' WHERE role='user'")
            # Ensure enum matches preferred casing and defaults
            cursor.execute("ALTER TABLE users MODIFY COLUMN role ENUM('User','Admin') NOT NULL DEFAULT 'User'")
            cursor.execute("ALTER TABLE users MODIFY COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE")
            try:
                cursor.execute("ALTER TABLE game_access MODIFY COLUMN is_allowed BOOLEAN DEFAULT FALSE")
            except Exception as _:
                pass

            # Migrate data from legacy user_profiles if present, then drop it
            cursor.execute(f"""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_schema = '{Config.MYSQL_DB}' AND table_name = 'user_profiles'
            """)
            if cursor.fetchone()[0]:
                cursor.execute("""
                    UPDATE users u
                    JOIN user_profiles p ON u.id = p.user_id
                    SET u.middlename = p.middlename,
                        u.birthday = p.birthdate,
                        u.age = p.age,
                        u.contact_number = p.contact_number
                """)
                cursor.execute("DROP TABLE user_profiles")
        except Exception as _:
            pass
        
        # 6. Seed Admin
        cursor.execute("SELECT * FROM users WHERE role = 'Admin'")
        if not cursor.fetchone():
            # Seed admin only when explicitly enabled via env var `SEED_ADMIN` and with `ADMIN_PASSWORD`
            seed_admin = os.environ.get('SEED_ADMIN', 'False').lower() in ('1', 'true', 'yes')
            admin_password = os.environ.get('ADMIN_PASSWORD')
            if seed_admin and admin_password:
                try:
                    from werkzeug.security import generate_password_hash
                    hashed = generate_password_hash(admin_password)
                    cursor.execute("""
                        INSERT INTO users (username, password, email, firstname, lastname, role, is_active)
                        VALUES ('admin', %s, 'admin@leafvillage.com', 'Super', 'Admin', 'Admin', TRUE)
                    """, (hashed,))
                    print("Seeded Admin account.")
                except Exception:
                    print("Failed to seed admin account.")
            else:
                print("Admin seed skipped. Set SEED_ADMIN=True and ADMIN_PASSWORD env vars to enable seeding.")


        conn.commit()
        print("Database initialized successfully.")
    except Error as e:
        print(f"Error initializing DB: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_db():
    conn = get_db_connection()
    if not conn:
        raise RuntimeError('Database unavailable')
    conn.database = Config.MYSQL_DB
    return conn

def log_audit_action(actor_id: int | None, target_user_id: int | None, action: str, details: str = "") -> None:
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO audit_logs (actor_id, target_user_id, action, details)
            VALUES (%s, %s, %s, %s)
            """,
            (actor_id, target_user_id, action, details)
        )
        conn.commit()
    except Error as e:
        print(f"Audit log insert failed: {e}")
    finally:
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass
