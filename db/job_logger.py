"""
Job logging functionality for tracking ETL and maintenance operations.
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default database path (relative to project root)
DEFAULT_DB_PATH = "db/dashboard.db"

# SQL to create the job_runs table if it doesn't exist
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS job_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_name TEXT NOT NULL,
    status TEXT NOT NULL,
    ran_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,
    duration_seconds REAL,
    details TEXT
);
"""

def get_db_connection(db_path: Optional[str] = None):
    """
    Get a database connection.
    
    Args:
        db_path: Path to the SQLite database file. If None, uses the default.
        
    Returns:
        sqlite3.Connection: Database connection
    """
    if db_path is None:
        # Use default path relative to project root
        db_path = str(Path(__file__).parent / "dashboard.db")
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    
    # Create tables if they don't exist
    with conn:
        conn.execute(CREATE_TABLE_SQL)
    
    return conn

def log_job(
    job_name: str,
    status: str,
    error_message: Optional[str] = None,
    duration: Optional[float] = None,
    details: Optional[Dict[str, Any]] = None,
    db_path: Optional[str] = None
) -> int:
    """
    Log a job run to the database.
    
    Args:
        job_name: Name of the job being run
        status: Status of the job (e.g., 'STARTED', 'SUCCESS', 'FAILED')
        error_message: Error message if the job failed
        duration: Duration of the job in seconds
        details: Additional details about the job run as a dictionary
        db_path: Path to the SQLite database file. If None, uses the default.
        
    Returns:
        int: The ID of the inserted job log entry
    """
    conn = get_db_connection(db_path)
    
    # Convert details dict to JSON string if provided
    details_json = None
    if details is not None:
        import json
        details_json = json.dumps(details, default=str)
    
    try:
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO job_runs 
                (job_name, status, error_message, duration_seconds, details)
                VALUES (?, ?, ?, ?, ?)
                """,
                (job_name, status, error_message, duration, details_json)
            )
            job_id = cursor.lastrowid
            
        logger.info(
            f"Logged job run: {job_name} - {status}" +
            (f" (Error: {error_message})" if error_message else "")
        )
        return job_id
        
    except Exception as e:
        logger.error(f"Failed to log job run: {e}", exc_info=True)
        raise
    finally:
        conn.close()

def get_job_history(
    job_name: Optional[str] = None,
    limit: int = 100,
    db_path: Optional[str] = None
) -> list:
    """
    Get a history of job runs.
    
    Args:
        job_name: Filter by job name. If None, returns all jobs.
        limit: Maximum number of records to return
        db_path: Path to the SQLite database file. If None, uses the default.
        
    Returns:
        list: List of job run records as dictionaries
    """
    conn = get_db_connection(db_path)
    
    try:
        query = """
            SELECT id, job_name, status, ran_at, error_message, duration_seconds
            FROM job_runs
        """
        params = []
        
        if job_name:
            query += " WHERE job_name = ?"
            params.append(job_name)
            
        query += " ORDER BY ran_at DESC LIMIT ?"
        params.append(limit)
        
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
        
    except Exception as e:
        logger.error(f"Failed to fetch job history: {e}", exc_info=True)
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    # Example usage
    job_id = log_job(
        job_name="TEST_JOB",
        status="SUCCESS",
        details={"message": "Test job completed successfully"}
    )
    print(f"Logged job with ID: {job_id}")
    
    # Get job history
    history = get_job_history(limit=5)
    print("\nRecent job runs:")
    for job in history:
        print(f"{job['ran_at']} - {job['job_name']}: {job['status']}")
