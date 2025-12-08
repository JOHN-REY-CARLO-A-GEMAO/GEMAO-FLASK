#!/usr/bin/env python3
"""
Database setup script for GEMAO-FLASK application
This script creates the database schema and populates it with sample data
"""

import mysql.connector
from mysql.connector import Error
import sys
import os

def read_sql_file(filename):
    """Read SQL file and return its content"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File {filename} not found")
        return None
    except Exception as e:
        print(f"Error reading file {filename}: {e}")
        return None

def execute_sql_script(connection, sql_content):
    """Execute SQL script content"""
    cursor = None
    try:
        cursor = connection.cursor()
        
        # Split SQL content into individual statements
        statements = []
        current_statement = ""
        
        for line in sql_content.split('\n'):
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('--'):
                continue
            current_statement += line + "\n"
            
            # If line ends with semicolon, it's the end of a statement
            if line.endswith(';'):
                statements.append(current_statement.strip())
                current_statement = ""
        
        # Add any remaining statement
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        # Execute each statement
        for statement in statements:
            if statement:
                try:
                    cursor.execute(statement)
                    connection.commit()
                except Error as e:
                    print(f"Error executing statement: {statement[:100]}...")
                    print(f"Error: {e}")
                    connection.rollback()
                    continue
        
        print(f"Successfully executed {len(statements)} SQL statements")
        return True
        
    except Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    finally:
        if cursor:
            cursor.close()

def create_connection():
    """Create database connection"""
    try:
        # Default MySQL connection settings
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # Update with your MySQL password
            autocommit=False
        )
        print("Successfully connected to MySQL server")
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        print("Please ensure MySQL is running and update connection settings")
        return None

def main():
    """Main function to set up database"""
    print("Starting GEMAO-FLASK database setup...")
    
    # Create connection
    connection = create_connection()
    if not connection:
        sys.exit(1)
    
    try:
        # Step 1: Create database schema
        print("\n=== Step 1: Creating database schema ===")
        schema_sql = read_sql_file('create_database.sql')
        if schema_sql:
            if execute_sql_script(connection, schema_sql):
                print("Database schema created successfully!")
            else:
                print("Failed to create database schema")
                sys.exit(1)
        
        # Step 2: Create leaderboard tables
        print("\n=== Step 2: Creating leaderboard tables ===")
        leaderboard_sql = read_sql_file('leaderboard_database.sql')
        if leaderboard_sql:
            if execute_sql_script(connection, leaderboard_sql):
                print("Leaderboard tables created successfully!")
            else:
                print("Failed to create leaderboard tables")
                sys.exit(1)
        
        # Step 3: Populate database with sample data
        print("\n=== Step 3: Populating database with sample data ===")
        populate_sql = read_sql_file('populate_database.sql')
        if populate_sql:
            if execute_sql_script(connection, populate_sql):
                print("Database populated successfully!")
            else:
                print("Failed to populate database")
                sys.exit(1)
        
        print("\n=== Database setup completed successfully! ===")
        
        # Display database statistics
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("USE gemao_db")
            
            tables = ['users', 'games', 'leaderboard_scores', 'user_personal_bests', 'audit_logs']
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                    result = cursor.fetchone()
                    print(f"{table}: {result['count']} records")
                except Error:
                    print(f"{table}: Table not found or error")
                    
        except Error as e:
            print(f"Error getting statistics: {e}")
        finally:
            cursor.close()
            
    except Exception as e:
        print(f"Unexpected error during setup: {e}")
        sys.exit(1)
    finally:
        if connection.is_connected():
            connection.close()
            print("Database connection closed")

if __name__ == "__main__":
    main()
