"""
Minimal Dash application to test if Dash is working correctly.
"""
from dash import Dash, html
import dash_bootstrap_components as dbc

def create_app():
    # Initialize the Dash app
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    # Define a simple layout
    app.layout = html.Div([
        html.H1("Dash Test Application"),
        html.P("If you can see this, Dash is working!"),
        dbc.Alert("Bootstrap is working!", color="success")
    ])
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run_server(debug=True, port=8050)
