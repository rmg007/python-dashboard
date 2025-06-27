"""
Callbacks for the Admin Dashboard audit log.
"""
from dash import Input, Output, State, html, ctx, no_update, dcc
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import json
import pandas as pd

from db.user_queries import get_admin_events, log_admin_event

def register_callbacks(app):
    """Register all audit log callbacks."""
    @app.callback(
        [Output("audit-table", "data"),
         Output("audit-table", "page_current"),
         Output("audit-loading-output", "children"),
         Output("audit-notification", "is_open"),
         Output("audit-notification", "children"),
         Output("audit-notification", "header"),
         Output("audit-notification", "icon")],
        [Input("refresh-audit-btn", "n_clicks"),
         Input("audit-date-range", "start_date"),
         Input("audit-date-range", "end_date"),
         Input("audit-event-type", "value"),
         Input("audit-user-filter", "value"),
         Input("audit-search", "value")],
        [State("audit-table", "page_current")],
        prevent_initial_call=True
    )
    def load_audit_events(refresh_click, start_date, end_date, event_types, users, search_term, current_page):
        """Load audit events based on filters."""
        ctx_callback = ctx.triggered[0]["prop_id"].split(".")[0]
        
        # Only trigger on initial load or when filters change
        if ctx_callback not in ["refresh-audit-btn", "audit-date-range.start_date", "audit-date-range.end_date", 
                               "audit-event-type", "audit-user-filter", "audit-search"] and ctx_callback != ".":
            raise PreventUpdate
        
        try:
            # Convert dates to datetime objects
            start_date = pd.to_datetime(start_date) if start_date else datetime.now() - timedelta(days=30)
            end_date = pd.to_datetime(end_date) if end_date else datetime.now()
            
            # Build query parameters
            params = {
                'start_date': start_date.strftime('%Y-%m-%d %H:%M:%S'),
                'end_date': end_date.strftime('%Y-%m-%d %H:%M:%S'),
                'event_types': event_types if event_types else None,
                'user_ids': users if users else None,
                'search': search_term.lower() if search_term else None,
                'limit': 10,
                'offset': (current_page or 0) * 10
            }
            
            # In a real app, you would fetch audit events from the database
            # For now, we'll use sample data
            sample_events = [
                {
                    'id': f'audit_{i}',
                    'timestamp': (datetime.now() - timedelta(hours=i)).strftime('%Y-%m-%d %H:%M:%S'),
                    'user_id': 'admin@example.com',
                    'event_type': 'user_updated',
                    'target_type': 'user',
                    'target_id': f'user_{i}',
                    'ip_address': '192.168.1.1',
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'metadata': json.dumps({
                        'field': 'role',
                        'old_value': 'user',
                        'new_value': 'admin'
                    })
                }
                for i in range(50)  # Generate 50 sample events
            ]
            
            # Apply filters
            filtered_events = []
            for event in sample_events:
                # Filter by date range
                event_time = datetime.strptime(event['timestamp'], '%Y-%m-%d %H:%M:%S')
                if event_time < start_date or event_time > end_date:
                    continue
                
                # Filter by event type
                if event_types and event['event_type'] not in event_types:
                    continue
                
                # Filter by user
                if users and event['user_id'] not in users:
                    continue
                
                # Filter by search term
                if search_term:
                    search = search_term.lower()
                    if (search not in event['user_id'].lower() and 
                        search not in event['event_type'].lower() and 
                        search not in event['target_type'].lower() and 
                        search not in event.get('metadata', '').lower()):
                        continue
                
                filtered_events.append(event)
            
            # Pagination
            total_events = len(filtered_events)
            start_idx = (current_page or 0) * 10
            end_idx = start_idx + 10
            paginated_events = filtered_events[start_idx:end_idx]
            
            # Format data for the table
            table_data = []
            for event in paginated_events:
                try:
                    metadata = json.loads(event.get('metadata', '{}'))
                except (json.JSONDecodeError, TypeError):
                    metadata = {}
                
                # Format details based on event type
                details = f"{event['event_type'].replace('_', ' ').title()}"
                if event['event_type'] == 'user_updated' and 'field' in metadata:
                    details = f"Updated {metadata['field']} from '{metadata.get('old_value', '')}' to '{metadata.get('new_value', '')}'"
                elif event['event_type'] == 'user_created':
                    details = f"Created user {event.get('target_id', '')}"
                elif event['event_type'] == 'user_deleted':
                    details = f"Deleted user {event.get('target_id', '')}"
                
                table_data.append({
                    'id': event['id'],
                    'timestamp': event['timestamp'],
                    'user_email': event['user_id'],
                    'event_type': event['event_type'].replace('_', ' ').title(),
                    'target_type': event['target_type'].title(),
                    'details': details,
                    'ip_address': event['ip_address']
                })
            
            return [
                table_data,  # Table data
                0,  # Reset to first page
                "",  # Clear loading output
                True,  # Show notification
                f"Loaded {len(table_data)} of {total_events} audit events",
                "Success",
                "success"
            ]
            
        except Exception as e:
            return [
                [],  # Empty table on error
                0,  # Reset to first page
                "",  # Clear loading output
                True,  # Show notification
                f"Error loading audit events: {str(e)}",
                "Error",
                "danger"
            ]
    
    @app.callback(
        Output("audit-user-filter", "options"),
        [Input("audit-table", "data")]
    )
    def update_user_options(table_data):
        """Update the user filter options based on the current data."""
        if not table_data:
            return []
        
        # Extract unique users from the current table data
        users = {}
        for row in table_data:
            user_email = row.get('user_email')
            if user_email and user_email not in users:
                users[user_email] = {'label': user_email, 'value': user_email}
        
        return list(users.values())
    
    @app.callback(
        Output("audit-event-details-modal", "is_open"),
        [Input("audit-table", "active_cell"),
         Input("close-audit-details", "n_clicks")],
        [State("audit-event-details-modal", "is_open"),
         State("audit-table", "data")],
        prevent_initial_call=True
    )
    def toggle_audit_details(active_cell, close_click, is_open, table_data):
        """Toggle the audit event details modal."""
        ctx_callback = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if ctx_callback == "audit-table.active_cell" and active_cell:
            # Open modal when a cell is clicked
            return [True]
        
        if ctx_callback == "close-audit-details.n_clicks" and close_click:
            # Close modal when close button is clicked
            return [False]
        
        return [is_open]
    
    @app.callback(
        Output("audit-event-details-content", "children"),
        [Input("audit-table", "active_cell")],
        [State("audit-table", "data")]
    )
    def update_audit_details(active_cell, table_data):
        """Update the audit event details modal content."""
        if not active_cell or not table_data:
            raise PreventUpdate
        
        # Get the row data for the active cell
        row_id = active_cell["row_id"]
        row_data = next((row for row in table_data if row.get("id") == row_id), None)
        
        if not row_data:
            return "No details available"
        
        # Create a details card
        card = dbc.Card([
            dbc.CardHeader([
                html.H5("Audit Event Details", className="mb-0")
            ]),
            dbc.CardBody([
                html.Dl(className="row mb-0", children=[
                    html.Dt("Timestamp", className="col-sm-3"),
                    html.Dd(row_data.get("timestamp", "N/A"), className="col-sm-9"),
                    
                    html.Dt("User", className="col-sm-3"),
                    html.Dd(row_data.get("user_email", "N/A"), className="col-sm-9"),
                    
                    html.Dt("Event Type", className="col-sm-3"),
                    html.Dd(row_data.get("event_type", "N/A"), className="col-sm-9"),
                    
                    html.Dt("Target Type", className="col-sm-3"),
                    html.Dd(row_data.get("target_type", "N/A"), className="col-sm-9"),
                    
                    html.Dt("IP Address", className="col-sm-3"),
                    html.Dd(row_data.get("ip_address", "N/A"), className="col-sm-9"),
                    
                    html.Dt("Details", className="col-sm-3"),
                    html.Dd(row_data.get("details", "No details available"), className="col-sm-9"),
                ])
            ])
        ])
        
        return card
