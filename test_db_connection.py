import os
import sys
import sqlite3
from pathlib import Path

def test_db_connection():
    print("Testing database connection...")
    
    # Get the database path
    db_path = os.path.join('data', 'app.db')
    db_dir = os.path.dirname(db_path)
    
    print(f"Database path: {os.path.abspath(db_path)}")
    print(f"Database directory exists: {os.path.exists(db_dir)}")
    
    # Ensure the data directory exists
    os.makedirs(db_dir, exist_ok=True)
    
    # Check if the database file exists
    db_exists = os.path.exists(db_path)
    print(f"Database file exists: {db_exists}")
    
    try:
        # Try to connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the database is writable
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        print(f"Database integrity check: {result[0] if result else 'Failed'}")
        
        # Check if we can create a table
        test_table = "test_table_123"
        cursor.execute(f"DROP TABLE IF EXISTS {test_table}")
        cursor.execute(f"CREATE TABLE {test_table} (id INTEGER PRIMARY KEY, name TEXT)")
        cursor.execute(f"INSERT INTO {test_table} (name) VALUES ('test')")
        cursor.execute(f"SELECT * FROM {test_table}")
        rows = cursor.fetchall()
        print(f"Test table created and data inserted. Rows: {rows}")
        
        # Clean up
        cursor.execute(f"DROP TABLE {test_table}")
        conn.commit()
        conn.close()
        
        print("✅ Database connection test passed")
        return True
        
    except Exception as e:
        print(f"❌ Database connection test failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_db_connection()
    sys.exit(0 if success else 1)
