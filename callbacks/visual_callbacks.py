from dash import Input, Output, callback, State
from db.queries import get_permit_trends, get_status_distribution, get_filtered_permits
from components.charts import build_trend_chart, build_status_chart
from components.datatable import build_permit_table

def register_visual_callbacks(app):
    """
    Register all visual callbacks for the dashboard.
    
    Args:
        app: The Dash application instance
    """
    @app.callback(
        [
            Output("chart-trend-container", "children"),
            Output("chart-status-container", "children"),
            Output("table-permits-container", "children"),
            Output("loading-output-1", "children"),
        ],
        [
            Input("filter-year", "value"),
            Input("filter-month", "value"),
            Input("filter-department", "value"),
        ],
        prevent_initial_call=False,
    )
    def update_visuals(year, month, dept):
        """
        Update all visual components based on filter selections.
        
        Args:
            year: Selected year filter value
            month: Selected month filter value
            dept: Selected department filter value
            
        Returns:
            tuple: Updated chart and table components
        """
        # Get data for each component
        trends_data = get_permit_trends(year, month, dept)
        status_data = get_status_distribution(year, month, dept)
        permits_data = get_filtered_permits(year, month, dept)
        
        # Build components with the filtered data
        trend_chart = build_trend_chart(trends_data)
        status_chart = build_status_chart(status_data)
        permit_table = build_permit_table(permits_data)
        
        # Return components in the correct order
        return (
            trend_chart,
            status_chart,
            permit_table,
            "",  # Empty string for loading component
        )
    
    @app.callback(
        Output("filter-month", "options"),
        Output("filter-month", "disabled"),
        Input("filter-year", "value")
    )
    def update_month_dropdown(selected_year):
        """
        Update month dropdown based on selected year.
        
        Args:
            selected_year: The selected year from the year dropdown
            
        Returns:
            tuple: Updated month options and disabled state
        """
        if not selected_year:
            return [], True
        
        # Generate all months (1-12) as options
        months = [
            {"label": month, "value": str(i).zfill(2)}
            for i, month in enumerate([
                "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"
            ], 1)
        ]
        
        return months, False
    
    # Add any additional visual callbacks here as needed
