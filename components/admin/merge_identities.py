"""
Merge Identities component for the Admin Dashboard.

Allows administrators to merge duplicate user accounts into a single canonical account.
"""
from dash import html, dcc, Input, Output, State, callback, no_update, dash_table
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from datetime import datetime
import pandas as pd

from db.user_queries import get_user, merge_users, log_admin_event

def build_merge_identities():
    """Build the merge identities interface."""
    return html.Div([
        html.Div(className="d-flex justify-content-between align-items-center mb-4", children=[
            html.H3("Merge User Identities", className="mb-0"),
            dbc.Button(
                [html.I(className="fas fa-question-circle me-2"), "Help"],
                id="merge-help-btn",
                color="link",
                className="text-muted"
            )
        ]),
        
        # Help alert
        dbc.Alert(
            [
                html.H4("About Merging Identities", className="alert-heading"),
                html.P("""
                    Use this tool to merge two user accounts into one. This is useful when a single user 
                    has multiple accounts (e.g., from different authentication providers) that should be 
                    consolidated into a single account.
                """),
                html.Hr(),
                html.P("""
                    The "Keep" account will be preserved, and all data from the "Merge" account will 
                    be transferred to it. The "Merge" account will be deactivated after the merge is complete.
                """, className="mb-0")
            ],
            id="merge-help-alert",
            color="info",
            is_open=False,
            dismissable=True,
            className="mb-4"
        ),
        
        # Merge form
        html.Div(className="card mb-4", children=[
            html.Div(className="card-body", children=[
                html.H5("Merge Users", className="card-title mb-4"),
                dbc.Row([
                    dbc.Col([
                        html.H6("Keep This Account", className="text-center mb-3"),
                        dbc.InputGroup([
                            dbc.InputGroupText("User ID or Email"),
                            dbc.Input(
                                id="keep-user-identifier",
                                placeholder="user@example.com",
                                type="text"
                            ),
                            dbc.Button("Find", id="find-keep-user", color="primary")
                        ], className="mb-2"),
                        dbc.Alert(
                            "User not found",
                            id="keep-user-not-found",
                            color="danger",
                            is_open=False,
                            dismissable=True,
                            className="mt-2"
                        ),
                        html.Div(id="keep-user-details", className="mt-3")
                    ], md=6, className="border-end"),
                    
                    dbc.Col([
                        html.H6("Merge Into It", className="text-center mb-3"),
                        dbc.InputGroup([
                            dbc.InputGroupText("User ID or Email"),
                            dbc.Input(
                                id="merge-user-identifier",
                                placeholder="user@example.com",
                                type="text"
                            ),
                            dbc.Button("Find", id="find-merge-user", color="primary")
                        ], className="mb-2"),
                        dbc.Alert(
                            "User not found",
                            id="merge-user-not-found",
                            color="danger",
                            is_open=False,
                            dismissable=True,
                            className="mt-2"
                        ),
                        html.Div(id="merge-user-details", className="mt-3")
                    ], md=6)
                ]),
                
                # Merge button
                html.Div(className="d-grid gap-2 mt-4", children=[
                    dbc.Button(
                        [html.I(className="fas fa-random me-2"), "Merge Accounts"],
                        id="merge-accounts-btn",
                        color="primary",
                        size="lg",
                        disabled=True,
                        className="w-100"
                    )
                ])
            ])
        ]),
        
        # Merge preview
        html.Div(className="card mb-4", children=[
            html.Div(className="card-body", children=[
                html.H5("Merge Preview", className="card-title mb-4"),
                html.Div(id="merge-preview", className="text-center text-muted")
            ])
        ]),
        
        # Merge confirmation modal
        dbc.Modal(
            [
                dbc.ModalHeader("Confirm Account Merge"),
                dbc.ModalBody([
                    html.P("You are about to merge the following accounts:", className="mb-3"),
                    html.Div(id="merge-confirmation-details"),
                    html.Hr(),
                    html.P("This action cannot be undone. Are you sure you want to continue?", className="mb-0")
                ]),
                dbc.ModalFooter([
                    dbc.Button("Cancel", id="cancel-merge", className="ms-auto", color="secondary"),
                    dbc.Button("Confirm Merge", id="confirm-merge", color="danger")
                ]),
            ],
            id="merge-confirm-modal",
            size="lg",
            is_open=False,
        ),
        
        # Merge success modal
        dbc.Modal(
            [
                dbc.ModalHeader("Merge Successful"),
                dbc.ModalBody([
                    html.Div(className="text-center mb-3", children=[
                        html.Div(className="mb-3", children=[
                            html.I(className="fas fa-check-circle text-success", style={"fontSize": "4rem"})
                        ]),
                        html.H4("Accounts Successfully Merged"),
                        html.P("The user accounts have been successfully merged.", className="text-muted")
                    ]),
                    html.Div(id="merge-success-details")
                ]),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-merge-success", className="ms-auto", color="primary")
                ),
            ],
            id="merge-success-modal",
            size="lg",
            is_open=False,
        ),
        
        # Hidden stores
        dcc.Store(id='keep-user-store'),
        dcc.Store(id='merge-user-store'),
        
        # Toast for notifications
        dbc.Toast(
            id="merge-notification",
            header="Notification",
            is_open=False,
            dismissable=True,
            duration=4000,
            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
        )
    ])

def build_user_card(user_data):
    """Build a card displaying user information."""
    if not user_data:
        return html.Div("No user selected", className="text-muted")
    
    return dbc.Card([
        dbc.CardBody([
            html.Div(className="d-flex align-items-center mb-3", children=[
                html.Div(className="me-3", children=[
                    html.Img(
                        src=user_data.get('avatar_url', '/static/images/default-avatar.png'),
                        className="rounded-circle",
                        style={"width": "64px", "height": "64px", "objectFit": "cover"}
                    )
                ]),
                html.Div(children=[
                    html.H5(user_data.get('full_name', 'No Name'), className="mb-1"),
                    html.P(user_data.get('email', 'No email'), className="text-muted mb-1"),
                    html.Span(
                        user_data.get('role', 'user').title(),
                        className=f"badge bg-{'primary' if user_data.get('role') == 'admin' else 'secondary'}"
                    )
                ])
            ]),
            html.Div(className="small text-muted", children=[
                html.Div([
                    html.Strong("User ID: "),
                    html.Span(user_data.get('user_id', 'N/A'), className="font-monospace small")
                ]),
                html.Div([
                    html.Strong("Provider: "),
                    html.Span(user_data.get('provider', 'N/A').title())
                ]),
                html.Div([
                    html.Strong("Created: "),
                    html.Span(
                        pd.to_datetime(user_data.get('created_at')).strftime('%Y-%m-%d')
                        if user_data.get('created_at') else 'N/A'
                    )
                ]),
                html.Div([
                    html.Strong("Last Login: "),
                    html.Span(
                        pd.to_datetime(user_data.get('last_login')).strftime('%Y-%m-%d %H:%M')
                        if user_data.get('last_login') else 'Never'
                    )
                ])
            ])
        ])
    ])

def register_callbacks(app):
    """Register callbacks for the merge identities component."""
    @app.callback(
        [Output("merge-help-alert", "is_open")],
        [Input("merge-help-btn", "n_clicks")],
        [State("merge-help-alert", "is_open")],
    )
    def toggle_help(n_clicks, is_open):
        """Toggle the help alert."""
        if n_clicks:
            return [not is_open]
        return [is_open]
    
    @app.callback(
        [Output("keep-user-details", "children"),
         Output("keep-user-not-found", "is_open"),
         Output("keep-user-store", "data")],
        [Input("find-keep-user", "n_clicks")],
        [State("keep-user-identifier", "value")]
    )
    def find_keep_user(n_clicks, identifier):
        """Find and display the user to keep."""
        if not n_clicks or not identifier:
            return [no_update] * 3
        
        # In a real app, you would look up the user in your database
        # For now, we'll use a mock user
        if "@" in identifier:  # Assume it's an email
            user = {
                'user_id': f"user_{identifier.split('@')[0]}",
                'email': identifier,
                'full_name': identifier.split('@')[0].title(),
                'role': 'user',
                'provider': 'email',
                'created_at': '2023-01-01T00:00:00',
                'last_login': '2023-05-15T14:30:00',
                'avatar_url': '/static/images/default-avatar.png'
            }
            return [build_user_card(user), False, user]
        
        # If user not found
        return [html.Div("No user details available", className="text-muted"), True, None]
    
    @app.callback(
        [Output("merge-user-details", "children"),
         Output("merge-user-not-found", "is_open"),
         Output("merge-user-store", "data")],
        [Input("find-merge-user", "n_clicks")],
        [State("merge-user-identifier", "value")]
    )
    def find_merge_user(n_clicks, identifier):
        """Find and display the user to merge."""
        if not n_clicks or not identifier:
            return [no_update] * 3
        
        # In a real app, you would look up the user in your database
        # For now, we'll use a mock user
        if "@" in identifier:  # Assume it's an email
            user = {
                'user_id': f"user_{identifier.split('@')[0]}_alt",
                'email': identifier,
                'full_name': identifier.split('@')[0].title(),
                'role': 'user',
                'provider': 'google',  # Different provider to simulate different account
                'created_at': '2023-02-15T00:00:00',
                'last_login': '2023-05-10T09:15:00',
                'avatar_url': '/static/images/default-avatar.png'
            }
            return [build_user_card(user), False, user]
        
        # If user not found
        return [html.Div("No user details available", className="text-muted"), True, None]
    
    @app.callback(
        [Output("merge-preview", "children"),
         Output("merge-accounts-btn", "disabled")],
        [Input("keep-user-store", "data"),
         Input("merge-user-store", "data")]
    )
    def update_merge_preview(keep_user, merge_user):
        """Update the merge preview based on selected users."""
        if not keep_user or not merge_user:
            return ["Select both users to see merge preview", True]
        
        if keep_user.get('user_id') == merge_user.get('user_id'):
            return ["Cannot merge the same user accounts", True]
        
        return [
            html.Div([
                html.P("The following data will be merged:", className="mb-3"),
                html.Ul(className="list-unstyled", children=[
                    html.Li(className="mb-2", children=[
                        html.I(className="fas fa-check-circle text-success me-2"),
                        "Profile information (name, email, etc.)"
                    ]),
                    html.Li(className="mb-2", children=[
                        html.I(className="fas fa-check-circle text-success me-2"),
                        "Authentication methods"
                    ]),
                    html.Li(className="mb-2", children=[
                        html.I(className="fas fa-check-circle text-success me-2"),
                        "User preferences and settings"
                    ]),
                    html.Li(className="mb-2", children=[
                        html.I(className="fas fa-check-circle text-success me-2"),
                        "Activity history and logs"
                    ]),
                    html.Li(children=[
                        html.I(className="fas fa-check-circle text-success me-2"),
                        "Permissions and roles"
                    ])
                ]),
                html.Div(className="alert alert-warning mt-3", children=[
                    html.Strong("Note: "),
                    " The second account will be deactivated after the merge."
                ])
            ]),
            False  # Enable the merge button
        ]
    
    @app.callback(
        [Output("merge-confirm-modal", "is_open"),
         Output("merge-confirmation-details", "children")],
        [Input("merge-accounts-btn", "n_clicks"),
         Input("cancel-merge", "n_clicks"),
         Input("confirm-merge", "n_clicks")],
        [State("keep-user-store", "data"),
         State("merge-user-store", "data"),
         State("merge-confirm-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_merge_modal(merge_click, cancel_click, confirm_click, keep_user, merge_user, is_open):
        """Toggle the merge confirmation modal."""
        ctx_callback = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if ctx_callback == "merge-accounts-btn" and merge_click:
            if not keep_user or not merge_user:
                raise PreventUpdate
                
            # Build confirmation details
            details = html.Div([
                html.Div(className="row", children=[
                    html.Div(className="col-md-6", children=[
                        html.Div(className="alert alert-success", children=[
                            html.H6("Keep This Account", className="alert-heading"),
                            html.P(keep_user.get('email', 'No email'), className="mb-1"),
                            html.P(f"User ID: {keep_user.get('user_id', 'N/A')}", className="small text-muted mb-0")
                        ])
                    ]),
                    html.Div(className="col-md-6", children=[
                        html.Div(className="alert alert-warning", children=[
                            html.H6("Merge and Deactivate", className="alert-heading"),
                            html.P(merge_user.get('email', 'No email'), className="mb-1"),
                            html.P(f"User ID: {merge_user.get('user_id', 'N/A')}", className="small text-muted mb-0")
                        ])
                    ])
                ]),
                html.Div(className="alert alert-info mt-3", children=[
                    html.Strong("After merging:", className="d-block mb-1"),
                    "• All data from the second account will be transferred to the first account\n",
                    "• The second account will be deactivated\n",
                    "• This action cannot be undone"
                ])
            ])
            
            return [True, details]
        
        if ctx_callback in ["cancel-merge", "confirm-merge"] and (cancel_click or confirm_click):
            return [False, no_update]
            
        return [is_open, no_update]
    
    @app.callback(
        [Output("merge-success-modal", "is_open"),
         Output("merge-success-details", "children")],
        [Input("confirm-merge", "n_clicks"),
         Input("close-merge-success", "n_clicks")],
        [State("keep-user-store", "data"),
         State("merge-user-store", "data"),
         State("merge-success-modal", "is_open")],
        prevent_initial_call=True
    )
    def handle_merge(confirm_click, close_click, keep_user, merge_user, is_open):
        """Handle the merge confirmation and show success modal."""
        ctx_callback = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if ctx_callback == "confirm-merge" and confirm_click:
            if not keep_user or not merge_user:
                raise PreventUpdate
            
            # In a real app, you would perform the merge operation here
            # merge_users(keep_user['user_id'], merge_user['user_id'])
            
            # Log the merge action
            log_admin_event(
                user_id=keep_user.get('user_id'),
                event_type="users_merged",
                target_type="user",
                target_id=merge_user.get('user_id'),
                metadata={
                    'kept_user': keep_user,
                    'merged_user': merge_user
                }
            )
            
            # Build success details
            details = html.Div([
                html.Div(className="alert alert-success", children=[
                    html.H5("Merge Summary", className="alert-heading"),
                    html.P("The following accounts have been successfully merged:", className="mb-2"),
                    html.Ul(className="mb-0", children=[
                        html.Li([
                            html.Strong("Kept Account: "),
                            f"{keep_user.get('email')} (ID: {keep_user.get('user_id')})"
                        ]),
                        html.Li([
                            html.Strong("Merged Account: "),
                            f"{merge_user.get('email')} (ID: {merge_user.get('user_id')})"
                        ])
                    ])
                ]),
                html.Div(className="alert alert-info mt-3", children=[
                    html.H5("Next Steps", className="alert-heading"),
                    html.Ul(className="mb-0", children=[
                        html.Li("The user can now log in using either authentication method"),
                        html.Li("All data has been consolidated into the kept account"),
                        html.Li("The merged account has been deactivated")
                    ])
                ])
            ])
            
            return [True, details]
        
        if ctx_callback == "close-merge-success" and close_click:
            return [False, no_update]
            
        return [is_open, no_update]
