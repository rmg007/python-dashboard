"""
User Management component for the Admin Dashboard.

Provides an interface for administrators to manage user accounts, roles, and permissions.
"""
from dash import html, dcc, dash_table, Input, Output, State, callback, ctx, no_update
import dash_bootstrap_components as dbc
from flask import session
import pandas as pd
from datetime import datetime

from db.user_queries import list_users, update_user, delete_user, log_admin_event
from layout.route_protect import admin_required, get_current_user

# Cache for user data to reduce database queries
_user_cache = {
    'last_updated': None,
    'users': None
}

def get_users(refresh: bool = False) -> list:
    """
    Get the list of users, with caching to reduce database load.
    
    Args:
        refresh: If True, force a refresh of the cache
        
    Returns:
        list: List of user dictionaries
    """
    global _user_cache
    
    # Return cached data if it's fresh (less than 5 minutes old)
    if not refresh and _user_cache['users'] and _user_cache['last_updated']:
        cache_age = (datetime.now() - _user_cache['last_updated']).total_seconds()
        if cache_age < 300:  # 5 minutes
            return _user_cache['users']
    
    # Fetch fresh data from the database
    users = list_users(active_only=False)
    
    # Update cache
    _user_cache['users'] = users
    _user_cache['last_updated'] = datetime.now()
    
    return users

def build_user_management():
    """Build the user management interface."""
    users = get_users(refresh=True)
    
    # Convert to DataFrame for the table
    df = pd.DataFrame(users)
    
    # Format dates
    if not df.empty:
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        df['last_login'] = pd.to_datetime(df['last_login']).dt.strftime('%Y-%m-%d %H:%M')
    
    return html.Div([
        html.Div(className="d-flex justify-content-between align-items-center mb-4", children=[
            html.H3("User Management", className="mb-0"),
            dbc.Button(
                [html.I(className="fas fa-sync-alt me-2"), "Refresh"],
                id="refresh-users-btn",
                color="primary",
                size="sm"
            )
        ]),
        
        # User table
        html.Div(className="card", children=[
            html.Div(className="card-body", children=[
                dash_table.DataTable(
                    id='users-table',
                    columns=[
                        {"name": "ID", "id": "user_id", "hideable": True},
                        {"name": "Email", "id": "email"},
                        {"name": "Name", "id": "full_name"},
                        {"name": "Role", "id": "role", "presentation": "dropdown"},
                        {"name": "Created", "id": "created_at"},
                        {"name": "Last Login", "id": "last_login"},
                        {"name": "Active", "id": "is_active", "presentation": "dropdown"},
                        {"name": "Actions", "id": "actions", "type": "text", "presentation": "markdown"}
                    ],
                    data=df.to_dict('records') if not df.empty else [],
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    row_selectable="multi",
                    selected_rows=[],
                    page_action="native",
                    page_current=0,
                    page_size=10,
                    style_table={"overflowX": "auto"},
                    style_cell={"textAlign": "left", "padding": "10px"},
                    style_header={
                        "backgroundColor": "rgb(248, 249, 250)",
                        "fontWeight": "bold"
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                        },
                        {
                            'if': {'column_editable': True},
                            'backgroundColor': 'rgba(25, 135, 84, 0.05)'
                        }
                    ],
                    dropdown={
                        'role': {
                            'options': [
                                {'label': 'User', 'value': 'user'},
                                {'label': 'Auditor', 'value': 'auditor'},
                                {'label': 'Admin', 'value': 'admin'}
                            ]
                        },
                        'is_active': {
                            'options': [
                                {'label': 'Active', 'value': True},
                                {'label': 'Inactive', 'value': False}
                            ]
                        }
                    }
                ),
                
                # Action buttons for selected rows
                html.Div(className="mt-3 d-flex gap-2", children=[
                    dbc.Button(
                        [html.I(className="fas fa-user-edit me-2"), "Edit Selected"],
                        id="edit-selected-users-btn",
                        color="primary",
                        size="sm",
                        disabled=True,
                        className="me-2"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-user-slash me-2"), "Deactivate"],
                        id="deactivate-users-btn",
                        color="warning",
                        size="sm",
                        disabled=True,
                        className="me-2"
                    ),
                    dbc.Button(
                        [html.I(className="fas fa-user-plus me-2"), "Add User"],
                        id="add-user-btn",
                        color="success",
                        size="sm",
                        className="ms-auto"
                    )
                ])
            ])
        ]),
        
        # Hidden div for storing data
        html.Div(id='user-management-data', style={'display': 'none'}),
        
        # Toast for notifications
        dbc.Toast(
            id="user-notification",
            header="Notification",
            is_open=False,
            dismissable=True,
            duration=4000,
            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
        )
    ])

def register_callbacks(app):
    """Register callbacks for the user management component."""
    @app.callback(
        [Output('users-table', 'data'),
         Output('users-table', 'selected_rows'),
         Output('users-table', 'selected_row_ids'),
         Output('user-notification', 'is_open'),
         Output('user-notification', 'children'),
         Output('user-notification', 'header'),
         Output('user-notification', 'icon'),
         Output('user-notification', 'className')],
        [Input('refresh-users-btn', 'n_clicks')],
        [State('users-table', 'data')]
    )
    def refresh_users(n_clicks, current_data):
        """Refresh the users table."""
        if n_clicks is None:
            return [no_update] * 8
            
        users = get_users(refresh=True)
        df = pd.DataFrame(users)
        
        if not df.empty:
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            df['last_login'] = pd.to_datetime(df['last_login']).dt.strftime('%Y-%m-%d %H:%M')
        
        return (
            df.to_dict('records') if not df.empty else [],
            [],  # Clear selected rows
            [],  # Clear selected row IDs
            True,  # Show notification
            f"Refreshed user list. Found {len(users)} users.",
            "Success",
            "success",
            "bg-success text-white"
        )
    
    @app.callback(
        [Output('edit-selected-users-btn', 'disabled'),
         Output('deactivate-users-btn', 'disabled')],
        [Input('users-table', 'selected_rows')]
    )
    def update_buttons(selected_rows):
        """Enable/disable action buttons based on selection."""
        if not selected_rows:
            return True, True
        return False, False
    
    @app.callback(
        [Output('edit-user-modal', 'is_open'),
         Output('edit-user-modal-body', 'children')],
        [Input('edit-selected-users-btn', 'n_clicks'),
         Input('edit-user-cancel', 'n_clicks'),
         Input('edit-user-save', 'n_clicks')],
        [State('users-table', 'selected_row_ids'),
         State('edit-user-modal', 'is_open')],
        prevent_initial_call=True
    )
    def toggle_edit_modal(edit_click, cancel_click, save_click, selected_ids, is_open):
        """Toggle the edit user modal."""
        ctx_callback = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if ctx_callback in ['edit-selected-users-btn', 'edit-user-save'] and not selected_ids:
            return no_update, no_update
            
        if ctx_callback == 'edit-user-save' and save_click:
            # Handle save logic here
            return False, no_update
            
        if ctx_callback == 'edit-user-cancel' or (ctx_callback == 'edit-user-save' and not save_click):
            return False, no_update
            
        # Show the edit form
        if selected_ids:
            # For now, just show a simple form
            form = dbc.Form([
                dbc.Row([
                    dbc.Label("Role", width=3),
                    dbc.Col([
                        dbc.Select(
                            id='edit-user-role',
                            options=[
                                {"label": "User", "value": "user"},
                                {"label": "Auditor", "value": "auditor"},
                                {"label": "Admin", "value": "admin"}
                            ],
                            value='user'
                        )
                    ], width=9)
                ], className="mb-3"),
                dbc.Row([
                    dbc.Label("Status", width=3),
                    dbc.Col([
                        dbc.Select(
                            id='edit-user-status',
                            options=[
                                {"label": "Active", "value": True},
                                {"label": "Inactive", "value": False}
                            ],
                            value=True
                        )
                    ], width=9)
                ], className="mb-3")
            ])
            
            return True, form
        
        return not is_open, no_update
