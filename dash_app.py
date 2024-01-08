import pandas as pd
import dash
from dash import html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

# Create a dash application
app = dash.Dash(__name__)

# Extract options from the DataFrame
options = [
    {"label": value, "value": value} for value in spacex_df["Launch Site"].unique()
]
options.insert(0, {"label": "All Sites", "value": "ALL"})

# Create an app layout
app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "color": "#503D36", "font-size": 40},
        ),
        dcc.Dropdown(
            id="site-dropdown",
            options=options,
            value="ALL",
            placeholder="Select a Launch Site here",
            searchable=True,
        ),
        html.Br(),
        # TASK 2: Add a pie chart to show the total successful launches count for all sites
        # If a specific launch site was selected, show the Success vs. Failed counts for the site
        html.Div(dcc.Graph(id="success-pie-chart")),
        html.Br(),
        html.P("Payload range (Kg):"),
        # TASK 3: Add a slider to select payload range
        dcc.RangeSlider(
            id="payload-slider",
            min=0,
            max=10000,
            step=1000,
            marks={i: str(i) for i in range(0, 10500, 500)},
            value=[min_payload, max_payload],
        ),
        # TASK 4: Add a scatter chart to show the correlation between payload and launch success
        html.Div(dcc.Graph(id="success-payload-scatter-chart")),
    ]
)


# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value"),
)
def get_pie_chart(entered_site):
    """
    Generates a pie chart showing the total successful launches count for all sites or
    the Success vs. Failed counts for a specific launch site based on user input.

    Parameters:
    - entered_site (str): The selected launch site.

    Returns:
    - plotly.graph_objs.Figure: The generated pie chart.
    """
    filtered_df = spacex_df
    if entered_site == "ALL":
        # Filter the DataFrame to include only successes (where 'class' is 1)
        filtered_df = spacex_df[spacex_df["class"] == 1]
        fig = px.pie(
            data_frame=filtered_df,
            names="Launch Site",
            title="Total Success Launches By Site",
        )
        return fig
    # Filter the DataFrame based on the selected site and create a pie chart
    filtered_df = filtered_df[filtered_df["Launch Site"] == entered_site]
    fig = px.pie(
        data_frame=filtered_df,
        names="class",
        title=f"Success vs. Failure for {entered_site}",
    )
    return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    [
        Input(component_id="site-dropdown", component_property="value"),
        Input(component_id="payload-slider", component_property="value"),
    ],
)
def get_scatter_chart(entered_site, selected_payload_range):
    """
    Generates a scatter chart showing the correlation between payload and launch success
    for all sites or a specific launch site based on user input.

    Parameters:
    - entered_site (str): The selected launch site.
    - selected_payload_range (list): The selected payload range.

    Returns:
    - plotly.graph_objs.Figure: The generated scatter chart.
    """
    # Check if the selected site is "ALL"
    if entered_site == "ALL":
        # No site-specific filtering
        filtered_df = spacex_df
        title = "Payload Success Correlation with Payload Mass (All Sites)"
    else:
        # Filter the DataFrame based on the selected site
        filtered_df = spacex_df[spacex_df["Launch Site"] == entered_site]
        title = f"Payload Success Correlation with Payload Mass ({entered_site})"

    # Filter the DataFrame based on the selected payload range
    filtered_df = filtered_df[
        (filtered_df["Payload Mass (kg)"] >= selected_payload_range[0])
        & (filtered_df["Payload Mass (kg)"] <= selected_payload_range[1])
    ]

    # Create a scatter chart
    fig = px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        title=title,
        labels={"class": "Launch Outcome", "Payload Mass (kg)": "Payload Mass"},
        category_orders={"class": ["Failure", "Success"]},
    )

    # Update y-axis ticks and rotate labels
    fig.update_yaxes(tickvals=[0, 1], ticktext=["Failure", "Success"], tickangle=-90)
    return fig


# Run the app
if __name__ == "__main__":
    app.run_server()
