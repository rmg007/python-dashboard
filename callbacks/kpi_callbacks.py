from dash import Input, Output, callback
from db.queries import get_kpi_totals

def register_kpi_callbacks(app):
    @app.callback(
        Output("kpi-total-permits", "children"),
        Output("kpi-total-valuation", "children"),
        Output("kpi-department-count", "children"),
        Input("filter-year", "value"),
        Input("filter-month", "value"),
        Input("filter-department", "value")
    )
    def update_kpis(year, month, department):
        # Get the totals from the database
        totals = get_kpi_totals(year, month, department)
        
        # Format the values with appropriate formatting
        if totals["total_permits"] == 0:
            return "No data", "—", "—"
            
        total_permits = f"{totals['total_permits']:,}"
        
        # Format currency, handling both string and numeric values
        valuation = totals['total_valuation']
        if isinstance(valuation, str):
            # Remove any existing currency symbols and commas
            valuation = valuation.replace('$', '').replace(',', '')
            try:
                valuation = float(valuation)
            except (ValueError, TypeError):
                valuation = 0.0
        
        total_valuation = f"${valuation:,.2f}" if valuation is not None else "$0.00"
        dept_count = f"{totals['department_count']}"

        return total_permits, total_valuation, dept_count
