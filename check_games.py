#!/usr/bin/env python3
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from MyFlaskapp.db import get_db

def main():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute('SELECT id, name, file_path FROM games ORDER BY name')
    games = cur.fetchall()
    cur.close()
    conn.close()
    
    print(f'Total games in database: {len(games)}')
    for game in games:
        print(f'  {game["id"]}: {game["name"]} ({game["file_path"]})')

if __name__ == "__main__":
    main()
