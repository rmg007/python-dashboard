from dash import html, dcc
from db.queries import get_filter_options

def build_sidebar():
    return html.Div([
        html.H5("Filters", className="mb-3"),

        dcc.Dropdown(
            id="filter-year",
            options=[{"label": str(y), "value": y} for y in get_filter_options("year")],
            placeholder="Year",
            className="mb-3"
        ),
        dcc.Dropdown(
            id="filter-month",
            options=[{"label": m, "value": m} for m in get_filter_options("month")],
            placeholder="Month",
            className="mb-3"
        ),
        dcc.Dropdown(
            id="filter-department",
            options=[{"label": d, "value": d} for d in get_filter_options("action_by_dept")],
            placeholder="Department"
        )
    ], id="sidebar-filters", style={"padding": "10px"})
