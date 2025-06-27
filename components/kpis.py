import dash_bootstrap_components as dbc
from dash import html

def get_kpi_placeholders():
    return dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("Total Permits", className="card-title"),
                html.H4("—", id="kpi-total-permits")
            ])
        ]), width=4),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("Total Valuation", className="card-title"),
                html.H4("—", id="kpi-total-valuation")
            ])
        ]), width=4),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("Departments", className="card-title"),
                html.H4("—", id="kpi-department-count")
            ])
        ]), width=4)
    ])
