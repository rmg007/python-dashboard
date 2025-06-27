from dash import html, dcc
from components.kpis import get_kpi_placeholders
from components.charts import build_trend_chart, build_status_chart
from components.datatable import build_permit_table

def build_main_panel():
    """
    Build the main panel with KPIs, charts, and data table.
    
    Returns:
        html.Div: A Div containing all the dashboard components
    """
    # Initialize empty data for charts and table
    empty_data = []
    
    return html.Div([
        # KPIs Row
        html.Div(
            get_kpi_placeholders(), 
            className="mb-4", 
            id="kpi-container"
        ),
        
        # Charts Row - Two columns for the charts
        html.Div([
            # Left column - Trend Chart
            html.Div(
                build_trend_chart(empty_data),
                className="chart-container mb-4",
                id="chart-trend-container"
            ),
            
            # Right column - Status Distribution
            html.Div(
                build_status_chart(empty_data),
                className="chart-container mb-4",
                id="chart-status-container"
            ),
        ], className="row"),
        
        # Data Table
        html.Div(
            build_permit_table(empty_data),
            className="table-container",
            id="table-permits-container"
        ),
        
        # Loading component for async updates
        dcc.Loading(
            id="loading-1",
            type="default",
            children=html.Div(id="loading-output-1")
        )
        
    ], id="main-panel", className="p-4")
