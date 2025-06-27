"""
Admin Dashboard for the Permit Dashboard application.

This module provides the admin interface for managing users, roles, and system settings.
"""
from dash import dcc, html, Input, Output, State, callback, dash_table, no_update
import dash_bootstrap_components as dbc
from flask import session
import pandas as pd

from layout.route_protect import admin_required, get_current_user
from db.user_queries import list_users, get_admin_events, log_admin_event

# Import admin components
from components.admin.user_management import build_user_management
from components.admin.session_logs import build_session_logs
from components.admin.audit_log import build_audit_log
from components.admin.merge_identities import build_merge_identities
from components.admin.layout_overrides import build_layout_overrides

# Register this page with the app
def register_callbacks(app):
    """Register all admin dashboard callbacks."""
    @app.callback(
        Output('admin-tabs-content', 'children'),
        [Input('admin-tabs', 'value')]
    )
    def render_tab(tab_value):
        """Render the selected admin tab content."""
        if tab_value == 'users':
            return build_user_management()
        elif tab_value == 'sessions':
            return build_session_logs()
        elif tab_value == 'audit':
            return build_audit_log()
        elif tab_value == 'merge':
            return build_merge_identities()
        elif tab_value == 'layout':
            return build_layout_overrides()
        return html.Div("Select a tab")
    
    # Import and register callbacks from components
    from components.admin.callbacks import register_callbacks as register_user_callbacks
    register_user_callbacks(app)
    
    from components.admin.audit_callbacks import register_callbacks as register_audit_callbacks
    register_audit_callbacks(app)
    
    from components.admin.merge_callbacks import register_callbacks as register_merge_callbacks
    register_merge_callbacks(app)

def layout():
    """Render the admin dashboard layout."""
    # Check if user is admin
    user = get_current_user()
    if not user or user.get('role') != 'admin':
        return html.Div(
            "Access Denied: Administrator privileges required.",
            className="alert alert-danger"
        )
    
    return html.Div([
        html.Div(className="admin-header", children=[
            html.H2("Admin Dashboard"),
            html.P(f"Welcome, {user.get('full_name', 'Administrator')}", className="text-muted")
        ]),
        
        dcc.Tabs(
            id="admin-tabs",
            value='users',
            className="mb-4",
            children=[
                dcc.Tab(label="User Management", value="users"),
                dcc.Tab(label="Session Logs", value="sessions"),
                dcc.Tab(label="Audit Log", value="audit"),
                dcc.Tab(label="Merge Identities", value="merge"),
                dcc.Tab(label="Layout Overrides", value="layout"),
            ]
        ),
        
        html.Div(id="admin-tabs-content"),
        
        # Store for admin data
        dcc.Store(id='admin-store'),
        
        # Modals
        html.Div([
            # User edit modal
            dbc.Modal(
                [
                    dbc.ModalHeader("Edit User"),
                    dbc.ModalBody(id='edit-user-modal-body'),
                    dbc.ModalFooter([
                        dbc.Button("Cancel", id="edit-user-cancel", className="ms-auto", color="secondary"),
                        dbc.Button("Save Changes", id="edit-user-save", className="ms-2", color="primary"),
                    ]),
                ],
                id="edit-user-modal",
                size="lg",
                is_open=False,
            ),
            # Delete confirmation modal
            dbc.Modal(
                [
                    dbc.ModalHeader("Confirm Deletion"),
                    dbc.ModalBody("Are you sure you want to delete this user? This action cannot be undone."),
                    dbc.ModalFooter([
                        dbc.Button("Cancel", id="delete-user-cancel", className="ms-auto", color="secondary"),
                        dbc.Button("Delete User", id="delete-user-confirm", className="ms-2", color="danger"),
                    ]),
                ],
                id="delete-user-modal",
                is_open=False,
            ),
        ]),
    ], className="p-4")
