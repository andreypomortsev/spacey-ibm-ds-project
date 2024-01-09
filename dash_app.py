"""
SpaceX Launch Dashboard

This module creates a Dash web application for visualizing SpaceX launch data.
It includes pie charts for showing the percentage of successful launches across all sites
and success vs. failure counts for a specific launch site. Additionally, it features
a scatter chart displaying the correlation between payload mass and launch success.

Dependencies:
- pandas
- dash
- plotly.express
- requests
- io
- colorcet

Data Source:
- SpaceX launch data is fetched from the following URL:
  https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/
  IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv

Usage:
- Run this module to start the Dash web application and navigate to the provided URL.

Authors:
- Yan Luo https://www.linkedin.com/in/yan-luo-96288783/
- Andrey Pomortsev https://www.linkedin.com/in/andreypomortsev/
"""
import io
import requests

import pandas as pd
import plotly.express as px

import dash
from dash import html
from dash.dependencies import Input, Output
import dash_core_components as dcc

import colorcet as cc


DATA_URL = (
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/"
    "IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"
)

try:
    response = requests.get(DATA_URL, timeout=2)
    response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
except requests.exceptions.RequestException as e:
    raise f"Error fetching or processing data from {DATA_URL}: {e}"

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv(io.BytesIO(response.content))
max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

# Define a custom colorblind-friendly palette for pie-chart
COLORS = ["#377eb8", "#ff7f00", "#f781bf", "#4daf4a"]

# Define a presumably colorblind-friendly palette for scatter plots
PALETTE = cc.glasbey_light

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
            title="Percentage of Successful Launches Across All Sites",
            color="Launch Site",
            color_discrete_map=dict(zip(filtered_df["Launch Site"].unique(), COLORS)),
        )
        return fig

    # Filter the DataFrame based on the selected site and create a pie chart
    filtered_df = filtered_df[filtered_df["Launch Site"] == entered_site]
    fig = px.pie(
        data_frame=filtered_df,
        names="class",
        title=f"Success vs. Failure for Launch Site: {entered_site}",
        color="class",
        color_discrete_map={1: COLORS[1], 0: COLORS[3]},
    )
    return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs,
# `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value"),
    Input(component_id="payload-slider", component_property="value"),
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
    else:
        # Filter the DataFrame based on the selected site
        filtered_df = spacex_df[spacex_df["Launch Site"] == entered_site]

    # Title
    title = (
        f"Site: {entered_site}, "
        f"Payload mass is between "
        f"{int(selected_payload_range[0]):8,d} kg and "
        f"{int(selected_payload_range[1]):8,d} kg"
    )

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
        category_orders={"class": [0, 1]},
        color_discrete_map=dict(
            zip(filtered_df["Booster Version Category"].unique(), PALETTE)
        ),
        size="Payload Mass (kg)",  # Add this line to set the size
    )

    # Update y-axis ticks and rotate labels
    fig.update_yaxes(tickvals=[0, 1], ticktext=["Failure", "Success"], tickangle=-90)
    return fig


# Run the app
if __name__ == "__main__":
    app.run_server()
