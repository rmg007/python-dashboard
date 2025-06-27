"""Database queries for export functionality."""
from typing import Dict, List, Any, Optional
from sqlalchemy import text
import json

def get_export_logs(db, user_id: str = None, limit: int = 100):
    """Retrieve export logs, optionally filtered by user."""
    with db.engine.connect() as conn:
        if user_id:
            result = conn.execute(
                text("""
                SELECT id, user_id, format, file_path, created_at, metadata
                FROM export_logs
                WHERE user_id = :user_id
                ORDER BY created_at DESC
                LIMIT :limit
                """),
                {"user_id": user_id, "limit": limit}
            )
        else:
            result = conn.execute(
                text("""
                SELECT id, user_id, format, file_path, created_at, metadata
                FROM export_logs
                ORDER BY created_at DESC
                LIMIT :limit
                """),
                {"limit": limit}
            )
        
        return [dict(row) for row in result.mappings()]

def log_export(db, export_data: Dict[str, Any]) -> int:
    """Log an export operation to the database."""
    with db.engine.connect() as conn:
        result = conn.execute(
            text("""
            INSERT INTO export_logs 
            (user_id, format, file_path, metadata)
            VALUES (:user_id, :format, :file_path, :metadata)
            RETURNING id
            """),
            {
                "user_id": export_data['user_id'],
                "format": export_data['format'],
                "file_path": export_data['file_path'],
                "metadata": json.dumps(export_data.get('metadata', {}))
            }
        )
        conn.commit()
        return result.scalar()

def get_export_schedules(db, user_id: str = None, active_only: bool = True):
    """Retrieve export schedules, optionally filtered by user and active status."""
    with db.engine.connect() as conn:
        query = """
        SELECT id, user_id, name, format, frequency, filters, 
               last_run, next_run, active, created_at
        FROM export_schedules
        WHERE 1=1
        """
        
        params = {}
        
        if user_id:
            query += " AND user_id = :user_id"
            params["user_id"] = user_id
            
        if active_only:
            query += " AND active = TRUE"
            
        query += " ORDER BY name"
        
        result = conn.execute(text(query), params)
        return [dict(row) for row in result.mappings()]

def create_export_schedule(db, schedule_data: Dict[str, Any]) -> int:
    """Create a new export schedule."""
    with db.engine.connect() as conn:
        result = conn.execute(
            text("""
            INSERT INTO export_schedules 
            (user_id, name, format, frequency, filters, next_run, active)
            VALUES (:user_id, :name, :format, :frequency, :filters, :next_run, :active)
            RETURNING id
            """),
            {
                "user_id": schedule_data['user_id'],
                "name": schedule_data['name'],
                "format": schedule_data['format'],
                "frequency": schedule_data['frequency'],
                "filters": json.dumps(schedule_data.get('filters', {})),
                "next_run": schedule_data.get('next_run'),
                "active": schedule_data.get('active', True)
            }
        )
        conn.commit()
        return result.scalar()

def update_export_schedule(db, schedule_id: int, updates: Dict[str, Any]) -> bool:
    """Update an existing export schedule."""
    if not updates:
        return False
        
    set_clauses = []
    params = {"id": schedule_id}
    
    if 'name' in updates:
        set_clauses.append("name = :name")
        params["name"] = updates['name']
        
    if 'format' in updates:
        set_clauses.append("format = :format")
        params["format"] = updates['format']
        
    if 'frequency' in updates:
        set_clauses.append("frequency = :frequency")
        params["frequency"] = updates['frequency']
        
    if 'filters' in updates:
        set_clauses.append("filters = :filters")
        params["filters"] = json.dumps(updates['filters'])
        
    if 'next_run' in updates:
        set_clauses.append("next_run = :next_run")
        params["next_run"] = updates['next_run']
        
    if 'active' in updates:
        set_clauses.append("active = :active")
        params["active"] = updates['active']
    
    if not set_clauses:
        return False
        
    with db.engine.connect() as conn:
        conn.execute(
            text(f"""
            UPDATE export_schedules
            SET {', '.join(set_clauses)},
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :id
            """),
            params
        )
        conn.commit()
        return True

def delete_export_schedule(db, schedule_id: int) -> bool:
    """Delete an export schedule."""
    with db.engine.connect() as conn:
        result = conn.execute(
            text("""
            DELETE FROM export_schedules
            WHERE id = :id
            RETURNING id
            """),
            {"id": schedule_id}
        )
        conn.commit()
        return bool(result.fetchone())

def get_export_presets(db, user_id: str):
    """Retrieve export presets for a user."""
    with db.engine.connect() as conn:
        result = conn.execute(
            text("""
            SELECT id, name, columns, filters, created_at
            FROM export_presets
            WHERE user_id = :user_id
            ORDER BY name
            """),
            {"user_id": user_id}
        )
        return [dict(row) for row in result.mappings()]

def save_export_preset(db, user_id: str, name: str, columns: list, filters: dict) -> int:
    """Save an export preset for a user."""
    with db.engine.connect() as conn:
        # Check if preset with this name already exists
        existing = conn.execute(
            text("""
            SELECT id FROM export_presets 
            WHERE user_id = :user_id AND name = :name
            """),
            {"user_id": user_id, "name": name}
        ).fetchone()
        
        if existing:
            # Update existing preset
            conn.execute(
                text("""
                UPDATE export_presets
                SET columns = :columns, 
                    filters = :filters,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :id
                """),
                {
                    "id": existing[0],
                    "columns": json.dumps(columns),
                    "filters": json.dumps(filters)
                }
            )
            conn.commit()
            return existing[0]
        else:
            # Insert new preset
            result = conn.execute(
                text("""
                INSERT INTO export_presets 
                (user_id, name, columns, filters)
                VALUES (:user_id, :name, :columns, :filters)
                RETURNING id
                """),
                {
                    "user_id": user_id,
                    "name": name,
                    "columns": json.dumps(columns),
                    "filters": json.dumps(filters)
                }
            )
            conn.commit()
            return result.scalar()

def delete_export_preset(db, preset_id: int, user_id: str) -> bool:
    """Delete an export preset."""
    with db.engine.connect() as conn:
        result = conn.execute(
            text("""
            DELETE FROM export_presets
            WHERE id = :id AND user_id = :user_id
            RETURNING id
            """),
            {"id": preset_id, "user_id": user_id}
        )
        conn.commit()
        return bool(result.fetchone())
