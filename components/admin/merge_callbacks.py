"""
Callbacks for the Admin Dashboard merge identities functionality.
"""
from dash import Input, Output, State, html, ctx, no_update, dcc
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import json

from db.user_queries import get_user, merge_users, log_admin_event

def register_callbacks(app):
    """Register all merge identities callbacks."""
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
         Output("merge-success-details", "children"),
         Output("merge-notification", "is_open"),
         Output("merge-notification", "children"),
         Output("merge-notification", "header"),
         Output("merge-notification", "icon")],
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
            
            try:
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
                
                return [
                    True,  # Show success modal
                    details,
                    True,  # Show notification
                    f"Successfully merged {merge_user.get('email')} into {keep_user.get('email')}",
                    "Merge Complete",
                    "success"
                ]
                
            except Exception as e:
                return [
                    False,  # Don't show success modal
                    no_update,
                    True,  # Show notification
                    f"Error merging accounts: {str(e)}",
                    "Error",
                    "danger"
                ]
        
        if ctx_callback == "close-merge-success" and close_click:
            return [False, no_update, no_update, no_update, no_update, no_update]
            
        return [is_open, no_update, no_update, no_update, no_update, no_update]

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
                        user_data.get('created_at', 'N/A')
                    )
                ]),
                html.Div([
                    html.Strong("Last Login: "),
                    html.Span(
                        user_data.get('last_login', 'Never')
                    )
                ])
            ])
        ])
    ])
