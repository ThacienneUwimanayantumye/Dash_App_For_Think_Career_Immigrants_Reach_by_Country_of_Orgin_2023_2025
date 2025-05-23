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
    html.H2("🌍 Interactive Mentor & Mentee Map by Country and Region",
            style={"textAlign": "center", "margin": "20px 0"}),

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

    dcc.Graph(id="map-graph", style={"height": "600px"})
])

@app.callback(
    Output("map-graph", "figure"),
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
        color_continuous_scale="reds",
        title=f"{role}s by Country ({region if region != 'ALL' else 'All Regions'})",
        projection="natural earth",
        hover_name="Country"
    )

    # Add annotations for total counts
    fig.add_annotation(
        x=0.01,
        y=0.01,
        xref="paper",
        yref="paper",
        text=f"Total {role}s: {total_people} | Total Countries: {total_countries}",
        showarrow=False,
        font=dict(
            size=14,
            color="#2c3e50"
        ),
        bgcolor="rgba(255, 255, 255, 0.8)",
        bordercolor="rgba(0, 0, 0, 0.2)",
        borderwidth=1,
        borderpad=4
    )

    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True),
        coloraxis_colorbar=dict(title="Count"),
        margin=dict(t=50, b=0, l=0, r=0)
    )

    return fig

# This is important for gunicorn
server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)
