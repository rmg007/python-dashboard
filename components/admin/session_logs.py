"""
Session Logs component for the Admin Dashboard.

Provides an interface for administrators to view and manage user sessions.
"""
from dash import html, dcc, Input, Output, State, callback, dash_table
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import pandas as pd

from db.user_queries import get_admin_events, log_admin_event

def build_session_logs():
    """Build the session logs interface."""
    # Default date range: last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    return html.Div([
        html.Div(className="d-flex justify-content-between align-items-center mb-4", children=[
            html.H3("Session Logs", className="mb-0"),
            dbc.Button(
                [html.I(className="fas fa-sync-alt me-2"), "Refresh"],
                id="refresh-sessions-btn",
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
                            id='session-date-range',
                            start_date=start_date.date(),
                            end_date=end_date.date(),
                            display_format='YYYY-MM-DD',
                            className="mb-3"
                        )
                    ], md=6),
                    dbc.Col([
                        dbc.Label("User"),
                        dcc.Dropdown(
                            id='session-user-filter',
                            placeholder="Filter by user...",
                            multi=True
                        )
                    ], md=6)
                ])
            ])
        ]),
        
        # Session logs table
        html.Div(className="card", children=[
            html.Div(className="card-body", children=[
                dash_table.DataTable(
                    id='sessions-table',
                    columns=[
                        {"name": "User", "id": "user_email"},
                        {"name": "Login Time", "id": "login_time"},
                        {"name": "Logout Time", "id": "logout_time"},
                        {"name": "Duration", "id": "duration"},
                        {"name": "IP Address", "id": "ip_address"},
                        {"name": "User Agent", "id": "user_agent"},
                        {"name": "Status", "id": "is_active"}
                    ],
                    data=[],
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
                            'if': {'column_id': 'is_active', 'filter_query': '{is_active} eq "Active"'},
                            'color': 'green',
                            'fontWeight': 'bold'
                        }
                    ]
                )
            ])
        ]),
        
        # Hidden div for storing data
        html.Div(id='sessions-data', style={'display': 'none'}),
        
        # Loading spinner
        dcc.Loading(
            id="sessions-loading",
            type="circle",
            children=html.Div(id="sessions-loading-output")
        ),
        
        # Toast for notifications
        dbc.Toast(
            id="sessions-notification",
            header="Notification",
            is_open=False,
            dismissable=True,
            duration=4000,
            style={"position": "fixed", "top": 66, "right": 10, "width": 350},
        )
    ])

def register_callbacks(app):
    """Register callbacks for the session logs component."""
    @app.callback(
        [Output('sessions-table', 'data'),
         Output('sessions-loading-output', 'children'),
         Output('sessions-notification', 'is_open'),
         Output('sessions-notification', 'children'),
         Output('sessions-notification', 'header'),
         Output('sessions-notification', 'icon')],
        [Input('refresh-sessions-btn', 'n_clicks'),
         Input('session-date-range', 'start_date'),
         Input('session-date-range', 'end_date'),
         Input('session-user-filter', 'value')],
        prevent_initial_call=True
    )
    def load_sessions(n_clicks, start_date, end_date, user_filter):
        """Load session data based on filters."""
        # Log the admin action
        log_admin_event(
            user_id="system",
            event_type="view_sessions",
            target_type="sessions",
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
            'user_ids': user_filter if user_filter else None
        }
        
        # In a real app, you would fetch session data from your database
        # For now, we'll return sample data
        sample_data = [
            {
                'user_email': 'admin@example.com',
                'login_time': (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S'),
                'logout_time': None,
                'duration': '1h 15m',
                'ip_address': '192.168.1.1',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'is_active': 'Active'
            },
            {
                'user_email': 'user@example.com',
                'login_time': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
                'logout_time': (datetime.now() - timedelta(days=1, hours=23)).strftime('%Y-%m-%d %H:%M:%S'),
                'duration': '15m',
                'ip_address': '192.168.1.2',
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
                'is_active': 'Inactive'
            }
        ]
        
        return (
            sample_data,
            "",  # Clear loading output
            True,  # Show notification
            f"Loaded {len(sample_data)} sessions",
            "Success",
            "success"
        )
    
    @app.callback(
        Output('session-user-filter', 'options'),
        [Input('refresh-sessions-btn', 'n_clicks')]
    )
    def load_user_options(n_clicks):
        """Load user options for the filter dropdown."""
        # In a real app, fetch distinct users with active sessions
        return [
            {'label': 'admin@example.com', 'value': 'admin@example.com'},
            {'label': 'user@example.com', 'value': 'user@example.com'}
        ]
