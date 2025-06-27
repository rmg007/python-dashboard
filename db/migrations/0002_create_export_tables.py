"""Create export-related tables."""
from datetime import datetime
from sqlalchemy import text

def upgrade(conn):
    # Create export logs table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS export_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        format TEXT NOT NULL,
        file_path TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        metadata TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)


    # Create export presets table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS export_presets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        name TEXT NOT NULL,
        columns TEXT,
        filters TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE(user_id, name)
    )
    """)

    # Create export schedules table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS export_schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        name TEXT NOT NULL,
        format TEXT NOT NULL,
        frequency TEXT NOT NULL,
        filters TEXT,
        last_run TIMESTAMP,
        next_run TIMESTAMP,
        active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE(user_id, name)
    )
    """)


    # Add indexes for better query performance
    conn.execute("CREATE INDEX IF NOT EXISTS idx_export_logs_user_id ON export_logs(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_export_logs_created_at ON export_logs(created_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_export_presets_user_id ON export_presets(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_export_schedules_user_id ON export_schedules(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_export_schedules_next_run ON export_schedules(next_run) WHERE active = 1")


def downgrade(conn):
    # Drop tables in reverse order to respect foreign key constraints
    conn.execute("DROP TABLE IF EXISTS export_schedules")
    conn.execute("DROP TABLE IF EXISTS export_presets")
    conn.execute("DROP TABLE IF EXISTS export_logs")
