"""
Callbacks for the Admin Dashboard session logs.
"""
from dash import Input, Output, State, html, ctx, no_update, dcc
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from datetime import datetime, timedelta
import pandas as pd

from db.user_queries import get_user_sessions, log_admin_event

def register_callbacks(app):
    """Register all session log callbacks."""
    @app.callback(
        [Output("sessions-table", "data"),
         Output("sessions-table", "page_current"),
         Output("sessions-loading", "children"),
         Output("sessions-notification", "is_open"),
         Output("sessions-notification", "children"),
         Output("sessions-notification", "header"),
         Output("sessions-notification", "icon")],
        [Input("refresh-sessions-btn", "n_clicks"),
         Input("sessions-date-range", "start_date"),
         Input("sessions-date-range", "end_date"),
         Input("sessions-user-filter", "value"),
         Input("sessions-status-filter", "value")],
        [State("sessions-table", "page_current")],
        prevent_initial_call=True
    )
    def load_sessions(refresh_click, start_date, end_date, user_filter, status_filter, current_page):
        """Load session data based on filters."""
        ctx_callback = ctx.triggered[0]["prop_id"].split(".")[0]
        
        # Only trigger on initial load or when filters change
        if ctx_callback not in ["refresh-sessions-btn", "sessions-date-range.start_date", 
                               "sessions-date-range.end_date", "sessions-user-filter", 
                               "sessions-status-filter"] and ctx_callback != ".":
            raise PreventUpdate
        
        try:
            # Convert dates to datetime objects
            start_date = pd.to_datetime(start_date) if start_date else datetime.now() - timedelta(days=7)
            end_date = pd.to_datetime(end_date) if end_date else datetime.now()
            
            # Format dates for display
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            
            # In a real app, you would fetch sessions from the database
            # For now, we'll generate some sample data
            sample_sessions = []
            for i in range(50):  # Generate 50 sample sessions
                session_time = datetime.now() - timedelta(hours=i*2)
                if not (start_date <= session_time <= end_date):
                    continue
                    
                user_id = f"user_{i % 5 + 1}@example.com"
                if user_filter and user_id != user_filter:
                    continue
                
                status = "active" if i % 5 != 0 else "expired"
                if status_filter and status not in status_filter:
                    continue
                
                sample_sessions.append({
                    'session_id': f'sess_{i}',
                    'user_id': user_id,
                    'ip_address': f'192.168.1.{i % 255}',
                    'user_agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.{i}.{i%100} Safari/537.36',
                    'created_at': session_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'expires_at': (session_time + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S'),
                    'last_activity': (session_time + timedelta(minutes=i % 60)).strftime('%Y-%m-%d %H:%M:%S'),
                    'status': status,
                    'device_type': 'Desktop' if i % 3 == 0 else 'Mobile' if i % 3 == 1 else 'Tablet',
                    'location': f'Location {i % 5 + 1}'
                })
            
            # Sort by last activity (newest first)
            sample_sessions.sort(key=lambda x: x['last_activity'], reverse=True)
            
            # Apply pagination
            page_size = 10
            start_idx = (current_page or 0) * page_size
            end_idx = start_idx + page_size
            paginated_sessions = sample_sessions[start_idx:end_idx]
            
            return [
                paginated_sessions,  # Table data
                0,  # Reset to first page
                "",  # Clear loading output
                True,  # Show notification
                f"Loaded {len(paginated_sessions)} sessions from {start_str} to {end_str}",
                "Session Logs Updated",
                "success"
            ]
            
        except Exception as e:
            return [
                [],  # Empty table on error
                0,  # Reset to first page
                "",  # Clear loading output
                True,  # Show notification
                f"Error loading sessions: {str(e)}",
                "Error",
                "danger"
            ]
    
    @app.callback(
        [Output("sessions-user-filter", "options"),
         Output("sessions-user-filter", "value")],
        [Input("sessions-table", "data")],
        [State("sessions-user-filter", "value")]
    )
    def update_user_filters(table_data, current_value):
        """Update the user filter options based on the current table data."""
        if not table_data:
            return [], None
        
        # Extract unique users from the current table data
        users = {}
        for row in table_data:
            user_id = row.get('user_id')
            if user_id and user_id not in users:
                users[user_id] = {'label': user_id, 'value': user_id}
        
        # Sort users by email
        user_options = sorted(users.values(), key=lambda x: x['label'])
        
        # Add an 'All Users' option
        options = [{'label': 'All Users', 'value': ''}] + user_options
        
        # Keep the current value if it's still valid
        valid_values = [opt['value'] for opt in options]
        value = current_value if current_value in valid_values else ''
        
        return [options, value]
    
    @app.callback(
        [Output("session-details-modal", "is_open"),
         Output("session-details-content", "children")],
        [Input("sessions-table", "active_cell"),
         Input("close-session-details", "n_clicks")],
        [State("session-details-modal", "is_open"),
         State("sessions-table", "data")],
        prevent_initial_call=True
    )
    def toggle_session_details(active_cell, close_click, is_open, table_data):
        """Toggle the session details modal."""
        ctx_callback = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if ctx_callback == "sessions-table.active_cell" and active_cell:
            # Get the row data for the active cell
            row_id = active_cell["row_id"]
            row_data = next((row for row in table_data if row.get("session_id") == row_id), None)
            
            if not row_data:
                return [False, "Session details not found"]
            
            # Create a details card
            details = dbc.Card([
                dbc.CardHeader([
                    html.Div(className="d-flex justify-content-between align-items-center", children=[
                        html.H5("Session Details", className="mb-0"),
                        dbc.Badge(
                            row_data.get("status", "unknown").title(),
                            color="success" if row_data.get("status") == "active" else "secondary",
                            className="text-uppercase"
                        )
                    ])
                ]),
                dbc.CardBody([
                    html.Div(className="row mb-4", children=[
                        html.Div(className="col-md-6", children=[
                            html.H6("Session Information", className="border-bottom pb-2"),
                            html.Dl(className="row mb-0", children=[
                                html.Dt("Session ID", className="col-sm-4"),
                                html.Dd(row_data.get("session_id", "N/A"), className="col-sm-8 text-muted"),
                                
                                html.Dt("User", className="col-sm-4"),
                                html.Dd(row_data.get("user_id", "N/A"), className="col-sm-8 text-muted"),
                                
                                html.Dt("Created", className="col-sm-4"),
                                html.Dd(row_data.get("created_at", "N/A"), className="col-sm-8 text-muted"),
                                
                                html.Dt("Last Activity", className="col-sm-4"),
                                html.Dd(row_data.get("last_activity", "N/A"), className="col-sm-8 text-muted"),
                                
                                html.Dt("Expires", className="col-sm-4"),
                                html.Dd(row_data.get("expires_at", "N/A"), className="col-sm-8 text-muted"),
                            ])
                        ]),
                        html.Div(className="col-md-6", children=[
                            html.H6("Device & Location", className="border-bottom pb-2"),
                            html.Dl(className="row mb-0", children=[
                                html.Dt("IP Address", className="col-sm-4"),
                                html.Dd(row_data.get("ip_address", "N/A"), className="col-sm-8 text-muted"),
                                
                                html.Dt("Device Type", className="col-sm-4"),
                                html.Dd(row_data.get("device_type", "N/A"), className="col-sm-8 text-muted"),
                                
                                html.Dt("Location", className="col-sm-4"),
                                html.Dd(row_data.get("location", "N/A"), className="col-sm-8 text-muted"),
                                
                                html.Dt("User Agent", className="col-sm-4"),
                                html.Dd(html.Small(
                                    row_data.get("user_agent", "N/A"),
                                    className="text-muted"
                                ), className="col-sm-8 text-muted"),
                            ])
                        ])
                    ]),
                    
                    html.H6("Session Actions", className="border-bottom pb-2 mb-3"),
                    html.Div(className="d-flex gap-2", children=[
                        dbc.Button(
                            [html.I(className="fas fa-sign-out-alt me-2"), "Terminate Session"],
                            color="danger",
                            size="sm",
                            disabled=row_data.get("status") != "active",
                            id={"type": "terminate-session-btn", "index": row_data.get("session_id")}
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-user-lock me-2"), "Logout User"],
                            color="warning",
                            size="sm",
                            disabled=row_data.get("status") != "active",
                            id={"type": "logout-user-btn", "index": row_data.get("user_id")}
                        ),
                        dbc.Button(
                            [html.I(className="fas fa-user-shield me-2"), "View User"],
                            color="primary",
                            size="sm",
                            outline=True,
                            id={"type": "view-user-btn", "index": row_data.get("user_id")}
                        )
                    ])
                ])
            ])
            
            return [True, details]
        
        if ctx_callback == "close-session-details.n_clicks" and close_click:
            return [False, no_update]
            
        return [is_open, no_update]
    
    @app.callback(
        [Output("terminate-session-alert", "is_open"),
         Output("terminate-session-alert", "children"),
         Output("terminate-session-alert", "color")],
        [Input({"type": "terminate-session-btn", "index": dash.dependencies.ALL}, "n_clicks")],
        [State("sessions-table", "data")],
        prevent_initial_call=True
    )
    def handle_terminate_session(terminate_clicks, table_data):
        """Handle session termination."""
        ctx_callback = ctx.triggered[0]["prop_id"]
        
        if not any(terminate_clicks) or not ctx_callback or not table_data:
            raise PreventUpdate
        
        # Extract session ID from the callback context
        session_id = ctx.triggered[0]["prop_id"].split("{\"index\":\"")[1].split("\"}")[0]
        
        try:
            # In a real app, you would terminate the session in your backend
            # For now, we'll just log the action
            log_admin_event(
                user_id="admin",  # Current admin user ID
                event_type="session_terminated",
                target_type="session",
                target_id=session_id,
                metadata={"action": "session_terminated"}
            )
            
            return [
                True,  # Show alert
                f"Session {session_id} has been terminated successfully.",
                "success"
            ]
        except Exception as e:
            return [
                True,  # Show alert
                f"Error terminating session: {str(e)}",
                "danger"
            ]
    
    @app.callback(
        [Output("logout-user-alert", "is_open"),
         Output("logout-user-alert", "children"),
         Output("logout-user-alert", "color")],
        [Input({"type": "logout-user-btn", "index": dash.dependencies.ALL}, "n_clicks")],
        prevent_initial_call=True
    )
    def handle_logout_user(logout_clicks):
        """Handle user logout from all devices."""
        ctx_callback = ctx.triggered[0]["prop_id"]
        
        if not any(logout_clicks) or not ctx_callback:
            raise PreventUpdate
        
        # Extract user ID from the callback context
        user_id = ctx.triggered[0]["prop_id"].split("{\"index\":\"")[1].split("\"}")[0]
        
        try:
            # In a real app, you would log the user out from all devices
            # For now, we'll just log the action
            log_admin_event(
                user_id="admin",  # Current admin user ID
                event_type="user_logged_out",
                target_type="user",
                target_id=user_id,
                metadata={"action": "force_logout_all_devices"}
            )
            
            return [
                True,  # Show alert
                f"User {user_id} has been logged out from all devices.",
                "success"
            ]
        except Exception as e:
            return [
                True,  # Show alert
                f"Error logging out user: {str(e)}",
                "danger"
            ]
