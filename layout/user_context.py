"""
User context management for the Permit Dashboard.

This module provides utilities for accessing the current user's context
and managing user-related data throughout the application.
"""
from typing import Optional, Dict, Any, Callable
from functools import wraps
import json
from flask import session, request
from dash import callback_context, no_update

# Import the database functions
from db.user_queries import get_user, log_session

def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Get the current user from the session.
    
    Returns:
        dict: User data if logged in, None otherwise
    """
    return session.get('user')

def get_user_id() -> Optional[str]:
    """
    Get the current user's ID.
    
    Returns:
        str: User ID if logged in, None otherwise
    """
    user = get_current_user()
    return user.get('user_id') if user else None

def get_user_role() -> Optional[str]:
    """
    Get the current user's role.
    
    Returns:
        str: User role if logged in, None otherwise
    """
    user = get_current_user()
    return user.get('role') if user else None

def is_authenticated() -> bool:
    """
    Check if the current user is authenticated.
    
    Returns:
        bool: True if user is logged in, False otherwise
    """
    return 'user' in session

def require_auth(view_func: Callable) -> Callable:
    """
    Decorator to ensure the user is authenticated.
    
    Args:
        view_func: The view function to protect
        
    Returns:
        function: Wrapped view function
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            # Store the requested URL to redirect after login
            if request.method == 'GET':
                session['next'] = request.url
            return {'error': 'Authentication required'}, 401
        return view_func(*args, **kwargs)
    return wrapper

def get_user_layout_override(user_id: Optional[str] = None) -> Optional[Dict]:
    """
    Get the layout override for a user.
    
    Args:
        user_id: Optional user ID. If not provided, uses the current user.
        
    Returns:
        dict: Layout override data if exists, None otherwise
    """
    if not user_id:
        user = get_current_user()
        if not user:
            return None
        user_id = user['user_id']
    
    user_data = get_user(user_id)
    if not user_data or not user_data.get('layout_override'):
        return None
    
    try:
        return json.loads(user_data['layout_override'])
    except (TypeError, json.JSONDecodeError):
        return None

def track_activity():
    """
    Track user activity by logging the current session.
    Should be called on page load or periodically.
    """
    if not is_authenticated():
        return
    
    user = get_current_user()
    if not user:
        return
    
    # Log the session with IP and user agent
    log_session(
        user_id=user['user_id'],
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )

def get_user_display_name(user: Optional[Dict] = None) -> str:
    """
    Get a display name for the user.
    
    Args:
        user: Optional user dictionary. If not provided, uses the current user.
        
    Returns:
        str: Display name
    """
    if user is None:
        user = get_current_user()
    
    if not user:
        return "Anonymous User"
    
    # Try to get the most appropriate name in order of preference
    if user.get('full_name'):
        return user['full_name']
    if user.get('email'):
        return user['email'].split('@')[0]  # Username part of email
    return user.get('user_id', 'Unknown User')

def get_user_avatar(user: Optional[Dict] = None) -> str:
    """
    Get the user's avatar URL.
    
    Args:
        user: Optional user dictionary. If not provided, uses the current user.
        
    Returns:
        str: URL to the user's avatar or a default avatar
    """
    if user is None:
        user = get_current_user()
    
    if not user:
        return "/static/images/default-avatar.png"
    
    return user.get('avatar_url', "/static/images/default-avatar.png")

def get_user_theme_preferences(user: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Get the user's theme preferences.
    
    Args:
        user: Optional user dictionary. If not provided, uses the current user.
        
    Returns:
        dict: Theme preferences
    """
    if user is None:
        user = get_current_user()
    
    # Default theme preferences
    default_prefs = {
        'theme': 'light',  # or 'dark', 'system'
        'density': 'comfortable',  # 'compact', 'comfortable', 'spacious'
        'font_size': 'medium',  # 'small', 'medium', 'large'
        'color_scheme': 'default',  # 'default', 'high_contrast', etc.
    }
    
    if not user:
        return default_prefs
    
    # In a real app, you might store these in the user's profile or preferences
    # For now, we'll just return the defaults
    return default_prefs

def get_user_timezone(user: Optional[Dict] = None) -> str:
    """
    Get the user's timezone.
    
    Args:
        user: Optional user dictionary. If not provided, uses the current user.
        
    Returns:
        str: Timezone string (e.g., 'America/New_York')
    """
    if user is None:
        user = get_current_user()
    
    # Default to UTC if not specified
    return user.get('timezone', 'UTC') if user else 'UTC'
