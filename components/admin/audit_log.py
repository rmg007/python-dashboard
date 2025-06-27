"""
Audit Log component for the Admin Dashboard.

Provides an interface for administrators to view and search audit logs.
"""
from dash import html, dcc, Input, Output, State, callback, dash_table, no_update
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import pandas as pd

from db.user_queries import get_admin_events, log_admin_event

def build_audit_log():
    """Build the audit log interface."""
    # Default date range: last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    return html.Div([
        html.Div(className="d-flex justify-content-between align-items-center mb-4", children=[
            html.H3("Audit Log", className="mb-0"),
            dbc.Button(
                [html.I(className="fas fa-sync-alt me-2"), "Refresh"],
                id="refresh-audit-btn",
                color="primary",
                size="sm"
            )
        ]),
        
        # Filters
        html.Div(className="card mb-4", children=[
            html.Div(className="card-body", children=[
                html.H5("Filters", className="card-title"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Date Range"),
                        dcc.DatePickerRange(
                            id='audit-date-range',
                            start_date=start_date.date(),
                            end_date=end_date.date(),
                            display_format='YYYY-MM-DD',
                            className="mb-3"
                        )
                    ], md=4),
                    dbc.Col([
                        dbc.Label("Event Type"),
                        dcc.Dropdown(
                            id='audit-event-type',
                            placeholder="Filter by event type...",
                            multi=True,
                            options=[
                                {'label': 'User Created', 'value': 'user_created'},
                                {'label': 'User Updated', 'value': 'user_updated'},
                                {'label': 'User Deleted', 'value': 'user_deleted'},
                                {'label': 'Role Changed', 'value': 'role_changed'},
                                {'label': 'Login', 'value': 'login'},
                                {'label': 'Logout', 'value': 'logout'},
                                {'label': 'Permission Changed', 'value': 'permission_changed'},
                                {'label': 'Settings Updated', 'value': 'settings_updated'}
                            ]
                        )
                    ], md=4),
                    dbc.Col([
                        dbc.Label("User"),
                        dcc.Dropdown(
                            id='audit-user-filter',
                            placeholder="Filter by user...",
                            multi=True
                        )
                    ], md=4)
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Search"),
                        dbc.Input(
                            id='audit-search',
                            type='text',
                            placeholder="Search in details..."
                        )
                    ], md=12)
                ], className="mt-3")
            ])
        ]),
        
        # Audit log table
        html.Div(className="card", children=[
            html.Div(className="card-body", children=[
                dash_table.DataTable(
                    id='audit-table',
                    columns=[
                        {"name": "Timestamp", "id": "timestamp"},
                        {"name": "User", "id": "user_email"},
                        {"name": "Event", "id": "event_type"},
                        {"name": "Target", "id": "target_type"},
                        {"name": "Details", "id": "details"},
                        {"name": "IP Address", "id": "ip_address"}
                    ],
                    data=[],  # Will be populated by callback
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    page_action="native",
                    page_current=0,
                    page_size=20,
                    style_table={"overflowX": "auto"},
                    style_cell={
                        'textAlign': 'left',
                        'padding': '10px',
                        'maxWidth': '300px',
                        'whiteSpace': 'normal',
                        'textOverflow': 'ellipsis',
                    },
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
                            'if': {
                                'filter_query': '{event_type} = "user_created" || {event_type} = "role_changed"',
                                'column_id': 'event_type'
                            },
                            'color': 'green',
                            'fontWeight': 'bold'
                        },
                        {
                            'if': {
                                'filter_query': '{event_type} = "user_deleted"',
                                'column_id': 'event_type'
                            },
                            'color': 'red',
                            'fontWeight': 'bold'
                        }
                    ]
                )
            ])
        ]),
        
        # Hidden div for storing data
        html.Div(id='audit-data', style={'display': 'none'}),
        
        # Loading spinner
        dcc.Loading(
            id="audit-loading",
            type="circle",
            children=html.Div(id="audit-loading-output")
        ),
        
        # Toast for notifications
        dbc.Toast(
            id="audit-notification",
            header="Notification",
            is_open=False,
            dismissable=True,
            duration=4000,
            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
        )
    ])

def register_callbacks(app):
    """Register callbacks for the audit log component."""
    @app.callback(
        [Output('audit-table', 'data'),
         Output('audit-loading-output', 'children'),
         Output('audit-notification', 'is_open'),
         Output('audit-notification', 'children'),
         Output('audit-notification', 'header'),
         Output('audit-notification', 'icon')],
        [Input('refresh-audit-btn', 'n_clicks'),
         Input('audit-date-range', 'start_date'),
         Input('audit-date-range', 'end_date'),
         Input('audit-event-type', 'value'),
         Input('audit-user-filter', 'value'),
         Input('audit-search', 'value')],
        prevent_initial_call=True
    )
    def load_audit_log(n_clicks, start_date, end_date, event_types, users, search_term):
        """Load audit log data based on filters."""
        # Log the admin action
        log_admin_event(
            user_id="system",
            event_type="view_audit_log",
            target_type="audit_log",
            ip_address=request.remote_addr if request else None,
            user_agent=request.user_agent.string if request and hasattr(request, 'user_agent') else None
        )
        
        # Convert dates to datetime objects
        start_date = pd.to_datetime(start_date).strftime('%Y-%m-%d 00:00:00')
        end_date = pd.to_datetime(end_date).strftime('%Y-%m-%d 23:59:59')
        
        # Build query parameters
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'event_types': event_types if event_types else None,
            'user_ids': users if users else None,
            'search': search_term if search_term else None
        }
        
        # In a real app, fetch audit data from your database
        # For now, we'll return sample data
        sample_data = [
            {
                'timestamp': (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
                'user_email': 'admin@example.com',
                'event_type': 'user_updated',
                'target_type': 'user',
                'details': 'Updated user role to admin',
                'ip_address': '192.168.1.1'
            },
            {
                'timestamp': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                'user_email': 'system',
                'event_type': 'user_created',
                'target_type': 'user',
                'details': 'New user registered: test@example.com',
                'ip_address': '192.168.1.2'
            },
            {
                'timestamp': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
                'user_email': 'admin@example.com',
                'event_type': 'settings_updated',
                'target_type': 'system',
                'details': 'Updated system settings',
                'ip_address': '192.168.1.1'
            }
        ]
        
        # Apply search filter if provided
        if search_term:
            search_term = search_term.lower()
            sample_data = [
                entry for entry in sample_data
                if (search_term in entry['user_email'].lower() or
                     search_term in entry['event_type'].lower() or
                     search_term in entry['details'].lower())
            ]
        
        return (
            sample_data,
            "",  # Clear loading output
            True,  # Show notification
            f"Loaded {len(sample_data)} audit events",
            "Success",
            "success"
        )
    
    @app.callback(
        Output('audit-user-filter', 'options'),
        [Input('refresh-audit-btn', 'n_clicks')]
    )
    def load_audit_user_options(n_clicks):
        """Load user options for the filter dropdown."""
        # In a real app, fetch distinct users from audit logs
        return [
            {'label': 'admin@example.com', 'value': 'admin@example.com'},
            {'label': 'system', 'value': 'system'}
        ]
    
    @app.callback(
        Output('audit-event-type', 'options'),
        [Input('audit-event-type', 'search_value')],
        [State('audit-event-type', 'value')]
    )
    def update_event_type_options(search_value, value):
        """Update event type options based on search input."""
        options = [
            {'label': 'User Created', 'value': 'user_created'},
            {'label': 'User Updated', 'value': 'user_updated'},
            {'label': 'User Deleted', 'value': 'user_deleted'},
            {'label': 'Role Changed', 'value': 'role_changed'},
            {'label': 'Login', 'value': 'login'},
            {'label': 'Logout', 'value': 'logout'},
            {'label': 'Permission Changed', 'value': 'permission_changed'},
            {'label': 'Settings Updated', 'value': 'settings_updated'}
        ]
        
        if not search_value:
            return options
            
        # Filter options based on search input
        search = search_value.lower()
        return [opt for opt in options if search in opt['label'].lower() or search in opt['value'].lower()]
