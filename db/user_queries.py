"""
Database queries for user management and authentication.
"""
from typing import List, Dict, Optional, Any, Union
import json
from datetime import datetime
from db.connection import get_connection

def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a user by their ID.
    
    Args:
        user_id: The user's unique identifier
        
    Returns:
        dict: User data if found, None otherwise
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, email, full_name, avatar_url, provider, 
                   role, layout_override, created_at, last_login, is_active
            FROM users 
            WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
            
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a user by their email address.
    
    Args:
        email: The user's email address
        
    Returns:
        dict: User data if found, None otherwise
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, email, full_name, avatar_url, provider, 
                   role, layout_override, created_at, last_login, is_active
            FROM users 
            WHERE email = ?
        """, (email,))
        
        row = cursor.fetchone()
        if not row:
            return None
            
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))

def create_user(user_data: Dict[str, Any]) -> str:
    """
    Create a new user.
    
    Args:
        user_data: Dictionary containing user data
        
    Returns:
        str: The ID of the created user
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (
                user_id, email, full_name, avatar_url, provider, 
                role, refresh_token, layout_override, is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                email = excluded.email,
                full_name = excluded.full_name,
                avatar_url = excluded.avatar_url,
                provider = excluded.provider,
                role = excluded.role,
                refresh_token = excluded.refresh_token,
                layout_override = excluded.layout_override,
                is_active = excluded.is_active
        """, (
            user_data['user_id'],
            user_data.get('email'),
            user_data.get('full_name'),
            user_data.get('avatar_url'),
            user_data.get('provider', 'local'),
            user_data.get('role', 'user'),
            user_data.get('refresh_token'),
            json.dumps(user_data.get('layout_override')) if user_data.get('layout_override') else None,
            user_data.get('is_active', True)
        ))
        conn.commit()
        return user_data['user_id']

def update_user(user_id: str, update_data: Dict[str, Any]) -> bool:
    """
    Update user data.
    
    Args:
        user_id: The ID of the user to update
        update_data: Dictionary containing fields to update
        
    Returns:
        bool: True if the update was successful, False otherwise
    """
    if not update_data:
        return False
        
    set_clause = ", ".join(f"{k} = ?" for k in update_data.keys())
    values = list(update_data.values())
    values.append(user_id)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            UPDATE users 
            SET {set_clause}
            WHERE user_id = ?
        """, values)
        conn.commit()
        return cursor.rowcount > 0

def delete_user(user_id: str) -> bool:
    """
    Delete a user.
    
    Args:
        user_id: The ID of the user to delete
        
    Returns:
        bool: True if the user was deleted, False otherwise
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount > 0

def list_users(role: Optional[str] = None, active_only: bool = True) -> List[Dict[str, Any]]:
    """
    List users with optional filtering.
    
    Args:
        role: Filter by role if provided
        active_only: If True, only return active users
        
    Returns:
        list: List of user dictionaries
    """
    query = """
        SELECT user_id, email, full_name, role, created_at, last_login, is_active
        FROM users
        WHERE 1=1
    """
    params = []
    
    if role:
        query += " AND role = ?"
        params.append(role)
        
    if active_only:
        query += " AND is_active = 1"
    
    query += " ORDER BY created_at DESC"
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def log_session(user_id: str, ip_address: str, user_agent: str) -> int:
    """
    Log a user session.
    
    Args:
        user_id: The ID of the user
        ip_address: The IP address of the user
        user_agent: The user agent string
        
    Returns:
        int: The ID of the created session
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        # First, mark any existing active sessions as inactive
        cursor.execute("""
            UPDATE user_sessions 
            SET is_active = 0 
            WHERE user_id = ? AND is_active = 1
        """, (user_id,))
        
        # Create new active session
        cursor.execute("""
            INSERT INTO user_sessions (user_id, ip_address, user_agent, is_active)
            VALUES (?, ?, ?, 1)
            RETURNING id
        """, (user_id, ip_address, user_agent))
        
        session_id = cursor.fetchone()[0]
        conn.commit()
        return session_id

def log_admin_event(user_id: str, event_type: str, target_type: Optional[str] = None, 
                   target_id: Optional[str] = None, ip_address: Optional[str] = None,
                   user_agent: Optional[str] = None, metadata: Optional[Dict] = None) -> int:
    """
    Log an admin event for audit purposes.
    
    Args:
        user_id: ID of the admin performing the action
        event_type: Type of event (e.g., 'user_created', 'role_updated')
        target_type: Type of the target (e.g., 'user', 'role')
        target_id: ID of the target entity
        ip_address: IP address of the admin
        user_agent: User agent string of the admin
        metadata: Additional metadata about the event
        
    Returns:
        int: The ID of the created event
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO admin_events 
            (user_id, event_type, target_type, target_id, ip_address, user_agent, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            RETURNING id
        """, (
            user_id,
            event_type,
            target_type,
            target_id,
            ip_address,
            user_agent,
            json.dumps(metadata) if metadata else None
        ))
        
        event_id = cursor.fetchone()[0]
        conn.commit()
        return event_id

def get_admin_events(limit: int = 100, offset: int = 0, 
                    user_id: Optional[str] = None, 
                    event_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve admin events with optional filtering.
    
    Args:
        limit: Maximum number of events to return
        offset: Number of events to skip
        user_id: Filter by admin user ID
        event_type: Filter by event type
        
    Returns:
        dict: Dictionary containing 'events' and 'total_count'
    """
    query = """
        SELECT ae.*, u.email as user_email, u.full_name as user_name
        FROM admin_events ae
        LEFT JOIN users u ON ae.user_id = u.user_id
        WHERE 1=1
    """
    count_query = "SELECT COUNT(*) FROM admin_events WHERE 1=1"
    params = []
    
    if user_id:
        query += " AND ae.user_id = ?"
        count_query += " AND user_id = ?"
        params.append(user_id)
        
    if event_type:
        query += " AND ae.event_type = ?"
        count_query += " AND event_type = ?"
        params.append(event_type)
    
    query += " ORDER BY ae.timestamp DESC LIMIT ? OFFSET ?"
    
    with get_connection() as conn:
        # Get total count
        cursor = conn.cursor()
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        
        # Get paginated results
        cursor.execute(query, params + [limit, offset])
        
        columns = [desc[0] for desc in cursor.description]
        events = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Parse metadata JSON
        for event in events:
            if event.get('metadata'):
                try:
                    event['metadata'] = json.loads(event['metadata'])
                except (json.JSONDecodeError, TypeError):
                    event['metadata'] = {}
        
        return {
            'events': events,
            'total_count': total_count,
            'limit': limit,
            'offset': offset
        }
