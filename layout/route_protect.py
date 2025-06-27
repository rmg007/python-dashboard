"""
Route protection and role-based access control for the Permit Dashboard.
"""
from functools import wraps
from typing import Callable, Optional, Any, Dict
from flask import request, redirect, url_for, session, flash, current_app
from dash import html

# Role hierarchy - higher number means more permissions
ROLE_HIERARCHY = {
    'admin': 3,
    'auditor': 2,
    'user': 1
}

def has_role(user_data: Optional[Dict], required_role: str) -> bool:
    """
    Check if a user has at least the required role.
    
    Args:
        user_data: Dictionary containing user data including 'role' key
        required_role: The minimum role required ('admin', 'auditor', or 'user')
        
    Returns:
        bool: True if the user has the required role or higher, False otherwise
    """
    if not user_data or 'role' not in user_data:
        return False
    
    user_role = user_data.get('role', 'user')
    
    # If the user's role or required role isn't in the hierarchy, deny access
    if user_role not in ROLE_HIERARCHY or required_role not in ROLE_HIERARCHY:
        return False
    
    return ROLE_HIERARCHY[user_role] >= ROLE_HIERARCHY[required_role]

def role_required(required_role: str = 'user'):
    """
    Decorator to protect routes with role-based access control.
    
    Args:
        required_role: Minimum role required to access the route
        
    Returns:
        function: Decorated route function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get user data from session or context
            user_data = session.get('user')
            
            if not user_data:
                # If user is not logged in, redirect to login
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login', next=request.url))
            
            # Check if user has the required role
            if not has_role(user_data, required_role):
                # If user doesn't have permission, show access denied
                return html.Div([
                    html.H3('Access Denied'),
                    html.P('You do not have permission to access this page.'),
                    html.A('Go back', href='/')
                ], className='container mt-5')
            
            # User has permission, proceed with the route
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Shortcut decorator for admin-only routes."""
    return role_required('admin')(f)

auditor_required = role_required('auditor')
login_required = role_required('user')

def get_current_user() -> Optional[Dict]:
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

def is_authenticated() -> bool:
    """
    Check if the current user is authenticated.
    
    Returns:
        bool: True if user is logged in, False otherwise
    """
    return 'user' in session

def get_user_role() -> Optional[str]:
    """
    Get the current user's role.
    
    Returns:
        str: User role if logged in, None otherwise
    """
    user = get_current_user()
    return user.get('role') if user else None

def has_permission(required_permission: str) -> bool:
    """
    Check if the current user has a specific permission.
    
    Args:
        required_permission: The permission to check (e.g., 'manage_users')
        
    Returns:
        bool: True if the user has the permission, False otherwise
    """
    user = get_current_user()
    if not user:
        return False
    
    # In a real app, you'd check against user permissions
    # For now, we'll just check the role
    user_role = user.get('role')
    
    # Define which roles have which permissions
    role_permissions = {
        'admin': ['manage_users', 'view_audit_logs', 'edit_settings'],
        'auditor': ['view_audit_logs'],
        'user': []
    }
    
    return required_permission in role_permissions.get(user_role, [])
