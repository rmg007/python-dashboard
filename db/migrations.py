"""
Database migration utilities for the Permit Dashboard application.
"""
import os
import sqlite3
from typing import List, Optional
from pathlib import Path
from datetime import datetime

# Get the absolute path to the database file
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.db")
MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "migrations")

def get_migration_files() -> List[str]:
    """
    Get all migration SQL files in the migrations directory.
    
    Returns:
        List of migration filenames, sorted by version number
    """
    if not os.path.exists(MIGRATIONS_DIR):
        return []
        
    migrations = []
    for filename in os.listdir(MIGRATIONS_DIR):
        if filename.endswith(".sql"):
            try:
                # Extract version number from filename (e.g., 001_initial.sql -> 1)
                version = int(filename.split("_")[0])
                migrations.append((version, filename))
            except (ValueError, IndexError):
                continue
    
    # Sort by version number
    return [m[1] for m in sorted(migrations, key=lambda x: x[0])]

def get_current_version(conn) -> int:
    """
    Get the current database version from the migrations table.
    
    Args:
        conn: SQLite database connection
        
    Returns:
        Current version number, or 0 if not initialized
    """
    try:
        cursor = conn.cursor()
        # Check if migrations table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='migrations'
        """)
        if not cursor.fetchone():
            return 0
            
        # Get the latest version
        cursor.execute("SELECT MAX(version) FROM migrations")
        result = cursor.fetchone()
        return result[0] if result and result[0] is not None else 0
    except sqlite3.Error as e:
        print(f"Error getting current version: {e}")
        return 0

def apply_migration(conn, filename: str) -> bool:
    """
    Apply a single migration file.
    
    Args:
        conn: SQLite database connection
        filename: Name of the migration file to apply
        
    Returns:
        bool: True if migration was successful, False otherwise
    """
    try:
        # Extract version number from filename
        version = int(filename.split("_")[0])
        
        # Read the migration SQL
        with open(os.path.join(MIGRATIONS_DIR, filename), 'r') as f:
            sql = f.read()
            
        # Execute the migration in a transaction
        cursor = conn.cursor()
        cursor.executescript(sql)
        
        # Record the migration
        cursor.execute("""
            INSERT INTO migrations (version, applied_at, filename)
            VALUES (?, ?, ?)
        """, (version, datetime.utcnow().isoformat(), filename))
        
        conn.commit()
        print(f"Applied migration: {filename}")
        return True
        
    except Exception as e:
        print(f"Error applying migration {filename}: {e}")
        conn.rollback()
        return False

def run_migrations() -> None:
    """
    Run all pending database migrations.
    """
    # Ensure migrations directory exists
    os.makedirs(MIGRATIONS_DIR, exist_ok=True)
    
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Create migrations table if it doesn't exist
        conn.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                version INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL,
                filename TEXT NOT NULL
            )
        """)
        
        # Get current version and available migrations
        current_version = get_current_version(conn)
        migrations = get_migration_files()
        
        if not migrations:
            print("No migrations found.")
            return
            
        # Apply pending migrations
        applied = 0
        for filename in migrations:
            version = int(filename.split("_")[0])
            if version > current_version:
                if apply_migration(conn, filename):
                    applied += 1
                else:
                    print(f"Failed to apply migration: {filename}")
                    break
        
        if applied > 0:
            print(f"Successfully applied {applied} migration(s)")
        else:
            print("Database is up to date")
            
    except Exception as e:
        print(f"Error running migrations: {e}")
        raise
        
    finally:
        conn.close()

if __name__ == "__main__":
    run_migrations()
