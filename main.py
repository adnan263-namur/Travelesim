import dash
from dash import dcc, html, Input, Output, State, ALL
import pandas as pd
import json
import webbrowser
import os
import urllib.parse

# Load the datasets
file_path = os.path.dirname(os.path.abspath(__file__))
# Load the datasets using relative paths
country_df = pd.read_excel(os.path.join(file_path, "Country.xlsx"), sheet_name="Country")
region_df = pd.read_excel(os.path.join(file_path, "Region.xlsx"), sheet_name="Region")


# Clean data (strip spaces and drop NaN values)
country_df.columns = country_df.columns.str.strip()
country_df = country_df.dropna()
region_df.columns = region_df.columns.str.strip()
region_df = region_df.dropna()


# Initialize Dash app with external stylesheet
app = dash.Dash(__name__, external_stylesheets=['/assets/styles.css'])


# App layout
app.layout = html.Div(
   style={
       "font-family": "Arial, sans-serif",
       "padding": "20px",
       "background": "linear-gradient(120deg, #e6e6fa 0%, #f3f3fd 100%)",
       "min-height": "100vh"
   },
   children=[
       # Title and subtitle
       html.Div(
           style={"text-align": "center"},
           children=[
               html.H1("Travel eSIM", style={"color": "#3c3c3c", "font-size": "36px", "margin-bottom": "0"}),
               html.P("powered by Imaginize", style={"color": "#666", "font-size": "14px", "margin-top": "5px"})
           ]
       ),


       # New dropdown for selecting between Country and Region
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


       # Dropdowns with responsive behavior
       html.Div([
           html.Label("Destination:", style={"font-weight": "bold", "margin-top": "10px"}),
           dcc.Dropdown(
               id='region-dropdown',
               placeholder="Choose a region",
               style={"width": "100%", "max-width": "500px", "margin": "10px auto"}
           ),
       ], style={"max-width": "600px", "margin": "0 auto"}),


       html.Div([
           html.Label("Data (GB):", style={"font-weight": "bold"}),
           dcc.Dropdown(
               id='data-dropdown',
               placeholder="Choose data",
               style={"width": "100%", "max-width": "500px", "margin": "10px auto"}
           ),
       ], style={"max-width": "600px", "margin": "0 auto"}),


       html.Div([
           html.Label("Validity (Days):", style={"font-weight": "bold"}),
           dcc.Dropdown(
               id='days-dropdown',
               placeholder="Choose validity",
               style={"width": "100%", "max-width": "500px", "margin": "10px auto"}
           ),
       ], style={"max-width": "600px", "margin": "0 auto"}),


       html.Div(id='data-table', style={"margin-top": "20px", "overflow-x": "auto"}),


       html.Button(
           "Order the eSIM now",
           id="order-button",
           n_clicks=0,
           disabled=True,  # Disabled until a row is selected
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
               "box-shadow": "0px 6px 15px rgba(0, 0, 0, 0.3)",  # More prominent shadow
               "transition": "all 0.3s ease",  # Smooth transition for hover effect
           }
       ),


       # Modal for user input
       html.Div(
           id="modal",
           style={
               "display": "none",  # Hidden by default
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
                   disabled=True,  # Disabled by default
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
                       "background-color": "#f44336",  # Red color for the "Close" button
                       "color": "white",
                       "border": "none",
                       "border-radius": "8px",
                       "cursor": "pointer",
                       "margin-top": "10px",  # Spacing between buttons
                   }
               ),
               # Warning message div
               html.Div(id="submit-warning", style={"color": "red", "text-align": "center", "margin-top": "10px"})
           ]
       ),


       # Backdrop for modal
       html.Div(
           id="modal-backdrop",
           style={
               "display": "none",  # Hidden by default
               "position": "fixed",
               "top": "0",
               "left": "0",
               "width": "100%",
               "height": "100%",
               "background-color": "rgba(0, 0, 0, 0.5)",
               "z-index": "999"
           }
       ),
       # Add this with your existing stores
       dcc.Store(id='selected-row-index-store', data=None),
       # Store to hold selected row data
       dcc.Store(id="selected-row-store", data={}),
       # Store to track form submission
       dcc.Store(id="form-submitted-store", data=False),
       dcc.Location(id='redirect-location', refresh=True)

   ]

)


# Update Region dropdown based on Dataset selection
@app.callback(
   Output('region-dropdown', 'options'),
   Input('dataset-dropdown', 'value')
)
def update_region_dropdown(selected_dataset):
   if selected_dataset == 'Country':
       df = country_df
   elif selected_dataset == 'Region':
       df = region_df
   else:
       return []
   return [{'label': r, 'value': r} for r in df['Region'].unique()]


# Update Data dropdown based on Region selection
@app.callback(
   Output('data-dropdown', 'options'),
   [Input('dataset-dropdown', 'value'),
    Input('region-dropdown', 'value')]
)
def update_data_dropdown(selected_dataset, selected_region):
   if not selected_dataset or not selected_region:
       return []


   if selected_dataset == 'Country':
       df = country_df
   elif selected_dataset == 'Region':
       df = region_df


   data_options = df.groupby('Region')['Data (GB)'].unique().to_dict()
   return [{'label': d, 'value': d} for d in data_options.get(selected_region, [])]


# Update Validity dropdown based on Data selection
@app.callback(
   Output('days-dropdown', 'options'),
   [Input('dataset-dropdown', 'value'),
    Input('region-dropdown', 'value'),
    Input('data-dropdown', 'value')]
)
def update_days_dropdown(selected_dataset, selected_region, selected_data):
   if not selected_dataset or not selected_region or not selected_data:
       return []


   if selected_dataset == 'Country':
       df = country_df
   elif selected_dataset == 'Region':
       df = region_df


   days_options = df.groupby(['Region', 'Data (GB)'])['Validity (Days)'].unique().to_dict()
   return [{'label': d, 'value': d} for d in days_options.get((selected_region, selected_data), [])]


# Update table based on selections and render clickable rows.
@app.callback(
   Output('data-table', 'children'),
   [Input('dataset-dropdown', 'value'),
    Input('region-dropdown', 'value'),
    Input('data-dropdown', 'value'),
    Input('days-dropdown', 'value')]
   [State('selected-row-index-store', 'data')]
)
def update_table(selected_dataset, selected_region, selected_data, selected_days, selected_index):
   try:
       if selected_dataset == 'Country':
           df = country_df
       elif selected_dataset == 'Region':
           df = region_df
       else:
           return html.Div("Please select Region for multiple countries OR Country for a single country", style={"color": "red"})


       filtered_df = df.copy()
       if selected_region:
           filtered_df = filtered_df[filtered_df['Region'] == selected_region]
       if selected_data:
           filtered_df = filtered_df[filtered_df['Data (GB)'] == selected_data]
       if selected_days:
           filtered_df = filtered_df[filtered_df['Validity (Days)'] == selected_days]


       # Define required columns for display; exclude "ID" from the table.
       display_columns = ['Name', 'Coverage', 'RRP info', 'Wi-Fi Hotspot', 'Traffic Policy']
       # Use only display_columns if available
       filtered_df = filtered_df[[col for col in display_columns if col in filtered_df.columns]]


       # Add Euro sign to RRP info if present
       if 'RRP info' in filtered_df.columns:
           filtered_df['RRP info'] = filtered_df['RRP info'].apply(lambda x: f"€{x}")


       table = html.Table(
           style={"width": "100%", "border-collapse": "collapse", "margin": "20px auto"},
           children=[
               html.Thead(
                   html.Tr([
                       html.Th(
                           col,
                           style={
                               "padding": "12px",
                               "border": "1px solid #ddd",
                               "background-color": "#6A4AE2",
                               "color": "white",
                               "cursor": "pointer"  # Add cursor indication
                           }
                       ) for col in filtered_df.columns
                   ])
               ),
               html.Tbody([
                   html.Tr(
                       id={"type": "table-row", "index": i},
                       children=[
                           html.Td(filtered_df.iloc[i][col], style={"padding": "8px", "border": "1px solid #ddd",
                                                                    "transition": "all 0.2s ease"})
                           for col in filtered_df.columns],
                        style={
                            "cursor": "pointer",
                            "background-color": "#89cbfa" if i == selected_index else "#f9f9f9"
                        },
                       n_clicks=0
                   ) for i in range(len(filtered_df))
               ])
           ]
       )
       return table
   except Exception as e:
       print(f"❌ Error in update_table: {e}")
       return html.Div("❌ An error occurred while updating the table.", style={"color": "red"})

# Enable/disable the "Order the eSIM now" button based on row selection.
@app.callback(
   Output('order-button', 'disabled'),
   Input({'type': 'table-row', 'index': ALL}, 'n_clicks')
)
def enable_order_button(row_clicks):
   # If any row has been clicked, enable the button.
   if any(click > 0 for click in row_clicks):
       return False
   return True


@app.callback(
    [Output('selected-row-index-store', 'data'),
     Output('selected-row-store', 'data')],
    [Input({'type': 'table-row', 'index': ALL}, 'n_clicks')],
    [State('selected-row-index-store', 'data'),
     State('dataset-dropdown', 'value'),
     State('region-dropdown', 'value'),
     State('data-dropdown', 'value'),
     State('days-dropdown', 'value')]
)
def handle_row_selection(clicks, current_index, dataset, region, data, days):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update

    # Get clicked row index
    try:
        triggered_id = json.loads(ctx.triggered[0]['prop_id'].split('.')[0])
        clicked_index = triggered_id['index']
    except:
        return dash.no_update, dash.no_update

    # Toggle selection if clicking the same row
    new_index = clicked_index if clicked_index != current_index else None

    # Get the corresponding row data
    if dataset == 'Country':
        df = country_df
    else:
        df = region_df
        
    try:
        filtered_df = df[(df['Region'] == region) & 
                        (df['Data (GB)'] == data) & 
                        (df['Validity (Days)'] == days)]
        row_data = filtered_df.iloc[clicked_index].to_dict() if new_index is not None else {}
    except:
        row_data = {}

    return new_index, row_data


   # Recreate filtered dataframe as in update_table.
   filtered_df = df.copy()
   if selected_region:
       filtered_df = filtered_df[filtered_df['Region'] == selected_region]
   if selected_data:
       filtered_df = filtered_df[filtered_df['Data (GB)'] == selected_data]
   if selected_days:
       filtered_df = filtered_df[filtered_df['Validity (Days)'] == selected_days]
   filtered_df = filtered_df.reset_index(drop=True)


   # Get the triggered row's id from the context.
   triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
   try:
       id_dict = json.loads(triggered_id)
   except Exception as e:
       return dash.no_update


   index = id_dict.get('index')
   if index is not None and index < len(filtered_df):
       return filtered_df.iloc[index].to_dict()
   return dash.no_update


# Show/hide modal and backdrop for user input.
@app.callback(
   [Output('modal', 'style'),
    Output('modal-backdrop', 'style')],
   [Input('order-button', 'n_clicks'),
    Input('close-button', 'n_clicks'),
    Input('submit-button', 'n_clicks')],
   [State('modal', 'style'),
    State('modal-backdrop', 'style')]
)
def toggle_modal(order_clicks, close_clicks, submit_clicks, modal_style, backdrop_style):
   ctx = dash.callback_context
   if not ctx.triggered:
       return modal_style, backdrop_style
   button_id = ctx.triggered[0]['prop_id'].split('.')[0]
   if button_id == "order-button" and order_clicks > 0:
       modal_style["display"] = "block"
       backdrop_style["display"] = "block"
   elif button_id in ["close-button", "submit-button"]:
       modal_style["display"] = "none"
       backdrop_style["display"] = "none"
   return modal_style, backdrop_style


# Enable/disable the Submit button based on form completion
@app.callback(
   Output('submit-button', 'disabled'),
   [Input('name-input', 'value'),
    Input('email-input', 'value'),
    Input('phone-input', 'value')]
)
def enable_submit(name, email, phone):
   # Disable the button if any field is empty
   return not all([name, email, phone])


# Show warning message if fields are incomplete
@app.callback(
   Output('submit-warning', 'children'),
   Input('submit-button', 'n_clicks'),
   [State('name-input', 'value'),
    State('email-input', 'value'),
    State('phone-input', 'value')]
)
def show_warning(submit_clicks, name, email, phone):
   if submit_clicks and not all([name, email, phone]):
       return "Please fill out the form first."
   return None


# Handle form submission and send email via mailto
@app.callback(
   Output('redirect-location', 'href'),
   Input('submit-button', 'n_clicks'),
   [State('name-input', 'value'),
    State('email-input', 'value'),
    State('phone-input', 'value'),
    State('dataset-dropdown', 'value'),
    State('region-dropdown', 'value'),
    State('data-dropdown', 'value'),
    State('days-dropdown', 'value'),
    State('selected-row-store', 'data')],
   prevent_initial_call=True  # Prevent callback from firing on initial load
)
def handle_submit(submit_clicks, name, email, phone, selected_dataset, region, data, days, selected_row):
    if submit_clicks > 0:
        # Check if all fields are filled
        if not all([name, email, phone]):
            return dash.no_update  # Do not proceed if any field is empty

        # Use selected_row to retrieve Traffic Policy and ID.
        traffic_policy = selected_row.get("Traffic Policy", "N/A") if selected_row else "N/A"
        id_value = selected_row.get("ID", "N/A") if selected_row else "N/A"
        order_summary = (
            f"Full Name: {name}\n"
            f"Email: {email}\n"
            f"Mobile number: {phone}\n"
            f"Dataset: {selected_dataset}\n"
            f"Region: {region}\n"
            f"Data: {data} GB\n"
            f"Validity: {days} Days\n"
            f"Traffic Policy: {traffic_policy}\n"
            f"<b>Price:</b> {selected_row.get('RRP info', 'N/A')}<br>"
            f"ID: {id_value}"
        )
        print(f"📝 Order Summary:\n{order_summary}")

        # URL-encode components
        encoded_subject = urllib.parse.quote(f"New order for eSIM for {region}")
        encoded_body = urllib.parse.quote(order_summary)

        outlook_url = f"https://outlook.office.com/mail/deeplink/compose?to=esimautomation@gmail.com&subject={encoded_subject}&body={encoded_body}"

        print(f"📧 Opening Outlook email composer: {outlook_url}")

        # Return a link component for redirection
        # return html.Script(f"window.location.href = '{outlook_url}';")
        return outlook_url
    return dash.no_update

app.run_server(host='0.0.0.0', port=8000, debug=False)
