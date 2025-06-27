from dash import dash_table, dcc, html
import pandas as pd
from typing import List, Tuple, Any

def build_permit_table(rows: List[Tuple[Any, ...]]) -> dash_table.DataTable:
    """
    Build an interactive DataTable showing permit records.
    
    Args:
        rows: List of tuples containing permit record data
        
    Returns:
        dash_table.DataTable: A Dash DataTable component with permit records
    """
    if not rows:
        return html.Div(
            "No permit data available for the selected filters.",
            className="no-data-message"
        )
    
    # Convert rows to DataFrame with appropriate column names
    columns = [
        "Permit Number", "Address", "Valuation", 
        "Date", "Task", "Status", "Department"
    ]
    
    df = pd.DataFrame(rows, columns=columns)
    
    # Format the valuation column to currency
    if not df.empty:
        df['Valuation'] = df['Valuation'].apply(
            lambda x: f"${float(x):,.2f}" if x and str(x).replace('.', '').isdigit() else x
        )
    
    # Format the date column
    if not df.empty and 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
    
    # Define column styles
    style_cell = {
        'fontFamily': 'Arial, sans-serif',
        'textAlign': 'left',
        'padding': '10px',
        'border': '1px solid #2A3F5F',
        'backgroundColor': '#1E2130',
        'color': '#7FDBFF',
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
        'maxWidth': 0,
    }
    
    style_header = {
        'backgroundColor': '#0E111F',
        'fontWeight': 'bold',
        'color': '#7FDBFF',
        'border': '1px solid #2A3F5F',
        'textAlign': 'center',
        'padding': '10px',
    }
    
    style_data_conditional = [
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': '#252A40',
        },
        {
            'if': {'state': 'active'},
            'backgroundColor': 'rgba(0, 116, 217, 0.3)',
            'border': '1px solid rgb(0, 116, 217)',
        },
    ]
    
    # Add conditional formatting for status column
    status_colors = {
        'Approved': '#2ecc71',
        'Pending': '#f39c12',
        'Rejected': '#e74c3c',
        'In Review': '#3498db',
        'Draft': '#9b59b6'
    }
    
    for status, color in status_colors.items():
        style_data_conditional.append({
            'if': {
                'filter_query': f'{{Status}} = "{status}"',
                'column_id': 'Status'
            },
            'color': color,
            'fontWeight': 'bold'
        })
    
    return html.Div([
        dash_table.DataTable(
            id='permit-table',
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            page_size=10,
            style_table={
                'overflowX': 'auto',
                'border': '1px solid #2A3F5F',
                'borderRadius': '5px',
                'overflow': 'hidden',
                'maxHeight': '600px',
            },
            style_cell=style_cell,
            style_header=style_header,
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
            },
            style_data_conditional=style_data_conditional,
            style_cell_conditional=[
                {'if': {'column_id': 'Permit Number'}, 'width': '12%'},
                {'if': {'column_id': 'Address'}, 'width': '20%'},
                {'if': {'column_id': 'Valuation'}, 'width': '10%', 'textAlign': 'right'},
                {'if': {'column_id': 'Date'}, 'width': '10%'},
                {'if': {'column_id': 'Task'}, 'width': '25%'},
                {'if': {'column_id': 'Status'}, 'width': '13%'},
                {'if': {'column_id': 'Department'}, 'width': '10%'},
            ],
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            page_action="native",
            style_as_list_view=True,
            tooltip_data=[
                {
                    column: {'value': str(value), 'type': 'markdown'}
                    for column, value in row.items()
                } for row in df.to_dict('records')
            ],
            tooltip_duration=None,
            export_format='csv',
            export_headers='display',
        ),
        # Add some custom CSS for the table
        html.Div([
            html.Style("""
                .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner table {
                    --accent: #1E2130;
                    --border: #2A3F5F;
                    --text-color: #7FDBFF;
                    --hover: rgba(0, 116, 217, 0.3);
                    --background-color: #1E2130;
                }
                .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner th {
                    background-color: #0E111F !important;
                }
                .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner td {
                    border-bottom: 1px solid var(--border);
                }
                .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner th.dash-filter {
                    background-color: #0E111F !important;
                }
                .dash-table-tooltip {
                    background-color: #1E2130 !important;
                    border: 1px solid #2A3F5F !important;
                    color: #7FDBFF !important;
                }
                .no-data-message {
                    color: #7FDBFF;
                    padding: 20px;
                    text-align: center;
                    font-style: italic;
                }
            """)
        ])
    ], className="datatable-container")
