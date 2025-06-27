"""
Database connection and initialization utilities for the Permit Dashboard.
"""
import os
import sqlite3
from typing import Optional, Callable, Any, Dict, List
from pathlib import Path

# Database file path
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
DB_PATH = os.path.join(DB_DIR, 'app.db')

# Ensure the data directory exists
os.makedirs(DB_DIR, exist_ok=True)

def get_connection() -> sqlite3.Connection:
    """
    Get a database connection.
    
    Returns:
        sqlite3.Connection: A connection to the SQLite database
    """
    conn = sqlite3.connect(DB_PATH)
    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")
    # Set a longer busy timeout to reduce the chance of database locks
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn

def init_db() -> None:
    """
    Initialize the database with required tables if they don't exist.
    """
    # Ensure the database directory exists
    os.makedirs(DB_DIR, exist_ok=True)
    
    # Create database file if it doesn't exist
    Path(DB_PATH).touch(exist_ok=True)
    
    # Run migrations to ensure the schema is up to date
    from .migrations import run_migrations
    run_migrations()

def execute_query(query: str, params: tuple = (), fetch: bool = False) -> Optional[list]:
    """
    Execute a SQL query and optionally return results.
    
    Args:
        query: SQL query to execute
        params: Parameters for the query
        fetch: Whether to fetch results
        
    Returns:
        List of results if fetch=True, None otherwise
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
        conn.commit()
        return None

def execute_script(script_path: str) -> None:
    """
    Execute a SQL script from a file.
    
    Args:
        script_path: Path to the SQL script file
    """
    with open(script_path, 'r') as f:
        sql = f.read()
    
    with get_connection() as conn:
        conn.executescript(sql)
        conn.commit()

def table_exists(table_name: str) -> bool:
    """
    Check if a table exists in the database.
    
    Args:
        table_name: Name of the table to check
        
    Returns:
        bool: True if the table exists, False otherwise
    """
    query = """
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name=?
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (table_name,))
        return cursor.fetchone() is not None
