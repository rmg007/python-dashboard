"""
Tests for the layout persistence and management functionality.
"""
import pytest
import sqlite3
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
import sys
sys.path.append(str(Path(__file__).parent.parent))

from db.connection import get_connection, init_db
from db.queries import get_user_layout, save_user_layout, get_default_layout
from layout.layout_manager import build_dashboard_layout, save_dashboard_layout, reset_dashboard_layout

# Test database path
TEST_DB = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_app.db')

def setup_module():
    """Set up test database before any tests run."""
    # Set test database path
    os.environ['TEST_DB'] = TEST_DB
    
    # Ensure test database directory exists
    os.makedirs(os.path.dirname(TEST_DB), exist_ok=True)
    
    # Initialize test database
    with patch('db.connection.DB_PATH', TEST_DB):
        # Create test tables
        conn = sqlite3.connect(TEST_DB)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS user_layouts (
            user_id TEXT,
            component_id TEXT,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            w INTEGER NOT NULL,
            h INTEGER NOT NULL,
            PRIMARY KEY (user_id, component_id)
        )
        """)
        conn.commit()
        conn.close()

def teardown_module():
    """Clean up after all tests have run."""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

class TestLayoutPersistence:
    """Test layout persistence functionality."""
    
    def setup_method(self):
        """Set up test data before each test method."""
        self.test_user = "test@example.com"
        self.test_layout = [
            {"i": "kpi-1", "x": 0, "y": 0, "w": 12, "h": 2},
            {"i": "chart-trend", "x": 0, "y": 2, "w": 6, "h": 3},
        ]
        
        # Clear test data before each test
        with get_connection() as conn:
            conn.execute("DELETE FROM user_layouts")
            conn.commit()
    
    def test_save_and_retrieve_layout(self):
        """Test saving and retrieving a user's layout."""
        # Save layout
        with patch('db.connection.DB_PATH', TEST_DB):
            result = save_user_layout(self.test_user, self.test_layout)
            assert result is None  # save_user_layout doesn't return anything
            
            # Retrieve layout
            saved_layout = get_user_layout(self.test_user)
            
            # Verify layout was saved correctly
            assert len(saved_layout) == 2
            assert saved_layout[0]["i"] == "kpi-1"
            assert saved_layout[1]["i"] == "chart-trend"
    
    def test_get_default_layout(self):
        """Test getting the default layout."""
        default_layout = get_default_layout()
        assert isinstance(default_layout, list)
        assert len(default_layout) > 0
        assert all(key in item for item in default_layout 
                  for key in ["i", "x", "y", "w", "h"])
    
    def test_build_dashboard_layout_new_user(self):
        """Test building layout for a new user (should use default)."""
        with patch('db.connection.DB_PATH', TEST_DB):
            layout_data = build_dashboard_layout("new_user@example.com")
            
            assert "layout" in layout_data
            assert "components" in layout_data
            assert "is_default" in layout_data
            assert layout_data["is_default"] is True
    
    def test_save_dashboard_layout(self):
        """Test saving a dashboard layout."""
        with patch('db.connection.DB_PATH', TEST_DB):
            # Save layout
            result = save_dashboard_layout(self.test_user, self.test_layout)
            assert result is True
            
            # Verify layout was saved
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM user_layouts WHERE user_id = ?", 
                    (self.test_user,)
                )
                count = cursor.fetchone()[0]
                assert count == 2  # 2 components in test layout
    
    def test_reset_dashboard_layout(self):
        """Test resetting a user's layout."""
        with patch('db.connection.DB_PATH', TEST_DB):
            # First save a layout
            save_dashboard_layout(self.test_user, self.test_layout)
            
            # Then reset it
            result = reset_dashboard_layout(self.test_user)
            assert result is True
            
            # Verify layout was reset (no entries for this user)
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM user_layouts WHERE user_id = ?", 
                    (self.test_user,)
                )
                count = cursor.fetchone()[0]
                assert count == 0
