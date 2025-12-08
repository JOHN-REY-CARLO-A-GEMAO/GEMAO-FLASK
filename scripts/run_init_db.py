"""
Small helper to initialize the database tables by calling
`MyFlaskapp.db.init_db_commands()` from the application.

Usage (PowerShell):
    py scripts\run_init_db.py

This script will use the same environment variables and `.env` loading
behavior as the application, so set `MYSQL_HOST`, `MYSQL_USER`,
`MYSQL_PASSWORD`, and `MYSQL_DB` as needed before running.
"""
import sys

if __name__ == '__main__':
    try:
        from MyFlaskapp.db import init_db_commands
    except Exception as e:
        print(f"Failed to import init_db_commands: {e}")
        sys.exit(2)

    try:
        init_db_commands()
        print("init_db_commands() finished. Check output above for any errors.")
    except Exception as e:
        print(f"init_db_commands() raised an exception: {e}")
        sys.exit(1)
