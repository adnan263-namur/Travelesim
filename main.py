import dash
from dash import dcc, html, Input, Output, State, ALL
import pandas as pd
import json
import os
import urllib.parse

# Load the datasets
file_path = os.path.dirname(os.path.abspath(__file__))
country_df = pd.read_excel(os.path.join(file_path, "Country.xlsx"), sheet_name="Country")
region_df = pd.read_excel(os.path.join(file_path, "Region.xlsx"), sheet_name="Region")

# Clean data (strip spaces and drop NaN values)
country_df.columns = country_df.columns.str.strip()
country_df = country_df.dropna()
region_df.columns = region_df.columns.str.strip()
region_df = region_df.dropna()

app = dash.Dash(__name__, external_stylesheets=['/assets/styles.css'])

app.layout = html.Div(
    style={
        "font-family": "Arial, sans-serif",
        "padding": "20px",
        "background": "linear-gradient(120deg, #e6e6fa 0%, #f3f3fd 100%)",
        "min-height": "100vh"
    },
    children=[
        dcc.Location(id='redirect-url', refresh=True),  # Added for VPS redirect

        # Title and subtitle
        html.Div(
            style={"text-align": "center"},
            children=[
                html.H1("Travel eSIM", style={"color": "#3c3c3c", "font-size": "36px", "margin-bottom": "0"}),
                html.P("powered by Imaginize", style={"color": "#666", "font-size": "14px", "margin-top": "5px"})
            ]
        ),

        # Dataset dropdown
        html.Div([
            html.Label("Single Country / Region:", style={"font-weight": "bold", "margin-top": "10px"}),
            dcc.Dropdown(
                id='dataset-dropdown',
                options=[
                    {'label': 'Country', 'value': 'Country'},
                    {'label': 'Region', 'value': 'Region'}
                ],
                placeholder="Choose a dataset",
                style={"width": "100%", "max-width": "500px", "margin": "10px auto"}
            ),
        ], style={"max-width": "600px", "margin": "0 auto"}),

        # Region dropdown
        html.Div([
            html.Label("Destination:", style={"font-weight": "bold", "margin-top": "10px"}),
            dcc.Dropdown(
                id='region-dropdown',
                placeholder="Choose a region",
                style={"width": "100%", "max-width": "500px", "margin": "10px auto"}
            ),
        ], style={"max-width": "600px", "margin": "0 auto"}),

        # Data dropdown
        html.Div([
            html.Label("Data (GB):", style={"font-weight": "bold"}),
            dcc.Dropdown(
                id='data-dropdown',
                placeholder="Choose data",
                style={"width": "100%", "max-width": "500px", "margin": "10px auto"}
            ),
        ], style={"max-width": "600px", "margin": "0 auto"}),

        # Days dropdown
        html.Div([
            html.Label("Validity (Days):", style={"font-weight": "bold"}),
            dcc.Dropdown(
                id='days-dropdown',
                placeholder="Choose validity",
                style={"width": "100%", "max-width": "500px", "margin": "10px auto"}
            ),
        ], style={"max-width": "600px", "margin": "0 auto"}),

        # Data table
        html.Div(id='data-table', style={"margin-top": "20px", "overflow-x": "auto"}),

        # Order button
        html.Button(
            "Order the eSIM now",
            id="order-button",
            n_clicks=0,
            disabled=True,
            style={
                "display": "block",
                "width": "200px",
                "margin": "20px auto",
                "padding": "12px",
                "font-size": "16px",
                "background-color": "#7c5cfc",
                "color": "white",
                "border": "none",
                "border-radius": "8px",
                "cursor": "pointer",
                "box-shadow": "0px 6px 15px rgba(0, 0, 0, 0.3)",
                "transition": "all 0.3s ease",
            }
        ),

        # Modal
        html.Div(
            id="modal",
            style={
                "display": "none",
                "position": "fixed",
                "top": "50%",
                "left": "50%",
                "transform": "translate(-50%, -50%)",
                "background-color": "white",
                "padding": "20px",
                "box-shadow": "0 4px 8px rgba(0, 0, 0, 0.2)",
                "z-index": "1000",
                "width": "300px",
                "border-radius": "10px"
            },
            children=[
                html.H3("Enter Your Details", style={"text-align": "center", "margin-bottom": "20px"}),
                html.Label("Name:", style={"font-weight": "bold"}),
                dcc.Input(id="name-input", type="text", placeholder="Your Name",
                          style={"width": "100%", "margin-bottom": "10px"}),
                html.Label("Email:", style={"font-weight": "bold"}),
                dcc.Input(id="email-input", type="email", placeholder="Your Email",
                          style={"width": "100%", "margin-bottom": "10px"}),
                html.Label("Mobile Number:", style={"font-weight": "bold"}),
                dcc.Input(id="phone-input", type="text", placeholder="Your Mobile Number",
                          style={"width": "100%", "margin-bottom": "20px"}),

                html.Button(
                    "Submit",
                    id="submit-button",
                    n_clicks=0,
                    disabled=True,
                    style={
                        "width": "100%",
                        "padding": "10px",
                        "font-size": "16px",
                        "background-color": "#7c5cfc",
                        "color": "white",
                        "border": "none",
                        "border-radius": "8px",
                        "cursor": "pointer",
                    }
                ),
                html.Button(
                    "Close",
                    id="close-button",
                    n_clicks=0,
                    style={
                        "width": "100%",
                        "padding": "10px",
                        "font-size": "16px",
                        "background-color": "#f44336",
                        "color": "white",
                        "border": "none",
                        "border-radius": "8px",
                        "cursor": "pointer",
                        "margin-top": "10px",
                    }
                ),
                html.Div(id="submit-warning", style={"color": "red", "text-align": "center", "margin-top": "10px"})
            ]
        ),

        # Backdrop
        html.Div(
            id="modal-backdrop",
            style={
                "display": "none",
                "position": "fixed",
                "top": "0",
                "left": "0",
                "width": "100%",
                "height": "100%",
                "background-color": "rgba(0, 0, 0, 0.5)",
                "z-index": "999"
            }
        ),
        dcc.Store(id="selected-row-store", data={})
    ]
)


# Keep all original callbacks unchanged until the submit handler

# ========== MODIFIED SUBMIT HANDLER ==========
@app.callback(
    Output('redirect-url', 'href'),
    Input('submit-button', 'n_clicks'),
    [State('name-input', 'value'),
     State('email-input', 'value'),
     State('phone-input', 'value'),
     State('dataset-dropdown', 'value'),
     State('region-dropdown', 'value'),
     State('data-dropdown', 'value'),
     State('days-dropdown', 'value'),
     State('selected-row-store', 'data')],
    prevent_initial_call=True
)
def handle_submit(submit_clicks, name, email, phone, selected_dataset, region, data, days, selected_row):
    if submit_clicks > 0:
        if not all([name, email, phone]):
            return dash.no_update

        # Construct VPS redirect URL with order parameters
        base_url = "http://your-vps-address/order-process"
        params = {
            'name': urllib.parse.quote(name),
            'email': urllib.parse.quote(email),
            'phone': urllib.parse.quote(phone),
            'dataset': urllib.parse.quote(selected_dataset),
            'region': urllib.parse.quote(region),
            'data': urllib.parse.quote(str(data)),
            'days': urllib.parse.quote(str(days)),
            'policy': urllib.parse.quote(selected_row.get("Traffic Policy", "")),
            'product_id': urllib.parse.quote(str(selected_row.get("ID", "")))
        }

        redirect_url = f"{base_url}?" + "&".join(
            [f"{k}={v}" for k, v in params.items()]
        )

        return redirect_url

    return dash.no_update


# Keep all other original callbacks exactly as they were
# (Region dropdown updates, table updates, modal toggles, etc.)

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8000, debug=False)