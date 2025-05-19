import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output

# --- Load Data ---
mentors = pd.read_excel("data/unique_mentors.xlsx")
mentees = pd.read_excel("data/unique_mentees.xlsx")

mentors["Role"] = "Mentor"
mentees["Role"] = "Mentee"

combined_data = pd.concat([
    mentors.rename(columns={"country_origin": "Country"}),
    mentees.rename(columns={"country_origin": "Country"})
])

combined_data["Country"] = combined_data["Country"].astype(str).str.strip()

# --- Map Regions ---
continent_map = {
    "Africa": ["Nigeria", "Kenya", "South Africa", "Egypt", "Ghana", "Morocco", "Tunisia", "Ethiopia", "Algeria", "Uganda"],
    "Asia": ["India", "China", "Japan", "Pakistan", "Bangladesh", "Indonesia", "Vietnam", "Philippines", "Thailand"],
    "Europe": ["France", "Germany", "UK", "United Kingdom", "Italy", "Spain", "Netherlands", "Sweden", "Switzerland"],
    "North America": ["United States", "Canada", "Mexico"],
    "South America": ["Brazil", "Argentina", "Colombia", "Chile", "Peru"],
    "Oceania": ["Australia", "New Zealand", "Fiji"],
    "Antarctica": [],
}

def assign_region(country):
    for region, countries in continent_map.items():
        if country in countries:
            return region
    return "Other"

combined_data["Region"] = combined_data["Country"].apply(assign_region)

# --- Create App ---
app = dash.Dash(__name__)

all_regions = ["Africa", "Asia", "Europe", "North America", "South America", "Oceania", "Antarctica", "Other"]

app.layout = html.Div([
    html.H2("🌍 Interactive Mentor & Mentee Map by Country and Region"),

    html.Div([
        html.Label("Select a Region:"),
        dcc.Dropdown(
            id="region-dropdown",
            options=[{"label": "All Regions", "value": "ALL"}] +
                    [{"label": r, "value": r} for r in all_regions],
            value="ALL",
            clearable=False
        ),

        html.Label("Select a Role:"),
        dcc.Dropdown(
            id="role-dropdown",
            options=[
                {"label": "Mentors", "value": "Mentor"},
                {"label": "Mentees", "value": "Mentee"},
            ],
            value="Mentor",
            clearable=False
        )
    ], style={"width": "30%", "display": "inline-block", "verticalAlign": "top"}),

    # Add total counts display at the top
    html.Div(id="total-counts", style={
        "textAlign": "center",
        "marginTop": "20px",
        "marginBottom": "20px",
        "fontSize": "20px",
        "fontWeight": "bold",
        "backgroundColor": "#f8f9fa",
        "padding": "15px",
        "borderRadius": "5px",
        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
    }),

    dcc.Graph(id="map-graph", style={"height": "600px"})
])

@app.callback(
    [Output("map-graph", "figure"),
     Output("total-counts", "children")],
    [Input("region-dropdown", "value"),
     Input("role-dropdown", "value")]
)
def update_map(region, role):
    filtered_df = combined_data[combined_data["Role"] == role]
    if region != "ALL":
        filtered_df = filtered_df[filtered_df["Region"] == region]

    country_counts = filtered_df["Country"].value_counts().reset_index()
    country_counts.columns = ["Country", "Count"]

    # Calculate totals
    total_people = filtered_df.shape[0]
    total_countries = len(filtered_df["Country"].unique())

    fig = px.choropleth(
        country_counts,
        locations="Country",
        locationmode="country names",
        color="Count",
        color_continuous_scale="Blues",
        title=f"{role}s by Country ({region if region != 'ALL' else 'All Regions'})",
        projection="natural earth",
        hover_name="Country"
    )

    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True),
        coloraxis_colorbar=dict(title="Count")
    )

    # Create the total counts display with more prominent styling
    total_counts_display = html.Div([
        html.Div([
            html.Span("Total number of ", style={"color": "#666"}),
            html.Span(f"{role}s: ", style={"color": "#2c3e50", "fontWeight": "bold"}),
            html.Span(f"{total_people}", style={"color": "#e74c3c", "fontWeight": "bold"})
        ]),
        html.Div([
            html.Span("Total number of countries: ", style={"color": "#666"}),
            html.Span(f"{total_countries}", style={"color": "#e74c3c", "fontWeight": "bold"})
        ])
    ])

    return fig, total_counts_display

# This is important for gunicorn
server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)
