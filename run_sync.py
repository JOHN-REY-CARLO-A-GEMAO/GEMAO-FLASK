#!/usr/bin/env python3
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from MyFlaskapp.sync import sync_games

def main():
    print("Starting game sync...")
    result = sync_games(1)  # Use user_id 1 as actor
    
    print(f"\nSync Results:")
    print(f"  Inserted: {result['inserted']}")
    print(f"  Updated: {result['updated']}")
    print(f"  Skipped: {result['skipped']}")
    print(f"  Errors: {result['errors']}")
    
    print(f"\nDetails:")
    for detail in result['details']:
        print(f"  {detail['file']}: {detail['action']}")
    
    print(f"\nTotal games processed: {len(result['details'])}")

if __name__ == "__main__":
    main()
