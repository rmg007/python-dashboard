-- Database schema for Permit Dashboard Admin Panel
-- Created: 2025-06-27

-- Enable WAL mode for better concurrency
PRAGMA journal_mode=WAL;

-- Users table to store all user information
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    provider TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'user', 'auditor')) DEFAULT 'user' NOT NULL,
    refresh_token TEXT,
    layout_override TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- User sessions for tracking logins
CREATE TABLE IF NOT EXISTS user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    logout_time TIMESTAMP,
    ip_address TEXT,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Admin events for audit logging
CREATE TABLE IF NOT EXISTS admin_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    target_type TEXT,
    target_id TEXT,
    ip_address TEXT,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,
    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- Track merged user accounts
CREATE TABLE IF NOT EXISTS merged_users (
    canonical_id TEXT NOT NULL,
    merged_id TEXT NOT NULL,
    merged_by TEXT NOT NULL,
    merged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,
    PRIMARY KEY (canonical_id, merged_id),
    FOREIGN KEY(canonical_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY(merged_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY(merged_by) REFERENCES users(user_id) ON DELETE SET NULL
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_time ON user_sessions(login_time);
CREATE INDEX IF NOT EXISTS idx_events_user ON admin_events(user_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON admin_events(timestamp);

-- Create default admin user (password: admin123 - change this in production!)
-- This is just for initial setup, should be changed immediately after first login
INSERT OR IGNORE INTO users (user_id, email, full_name, provider, role, is_active)
VALUES (
    'admin@localhost',
    'admin@localhost',
    'System Administrator',
    'local',
    'admin',
    1
);

-- Create a trigger to update last_login timestamp on new session
CREATE TRIGGER IF NOT EXISTS update_last_login
AFTER INSERT ON user_sessions
FOR EACH ROW
WHEN NEW.is_active = 1
BEGIN
    UPDATE users 
    SET last_login = CURRENT_TIMESTAMP 
    WHERE user_id = NEW.user_id;
END;
