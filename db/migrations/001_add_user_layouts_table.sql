-- Migration to add user_layouts table for Phase 4
-- This table stores the layout configuration for each user's dashboard

BEGIN TRANSACTION;

-- Create user_layouts table if it doesn't exist
CREATE TABLE IF NOT EXISTS user_layouts (
    user_id TEXT NOT NULL,
    component_id TEXT NOT NULL,
    x INTEGER NOT NULL,
    y INTEGER NOT NULL,
    w INTEGER NOT NULL,
    h INTEGER NOT NULL,
    PRIMARY KEY (user_id, component_id)
);

-- Create index for faster lookups by user_id
CREATE INDEX IF NOT EXISTS idx_user_layouts_user_id ON user_layouts(user_id);

COMMIT;
