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

# Mobile-friendly layout
app.layout = html.Div([
    # Title with responsive font size
    html.H2("🌍 Interactive Mentor & Mentee Map by Country and Region",
            style={
                "textAlign": "center",
                "fontSize": "clamp(1.5rem, 5vw, 2rem)",
                "margin": "10px 0"
            }),

    # Controls container with responsive width
    html.Div([
        html.Div([
            html.Label("Select a Region:",
                      style={"fontSize": "clamp(0.9rem, 3vw, 1.1rem)"}),
            dcc.Dropdown(
                id="region-dropdown",
                options=[{"label": "All Regions", "value": "ALL"}] +
                        [{"label": r, "value": r} for r in all_regions],
                value="ALL",
                clearable=False,
                style={"fontSize": "clamp(0.8rem, 2.5vw, 1rem)"}
            ),
        ], style={"marginBottom": "15px"}),

        html.Div([
            html.Label("Select a Role:",
                      style={"fontSize": "clamp(0.9rem, 3vw, 1.1rem)"}),
            dcc.Dropdown(
                id="role-dropdown",
                options=[
                    {"label": "Mentors", "value": "Mentor"},
                    {"label": "Mentees", "value": "Mentee"},
                ],
                value="Mentor",
                clearable=False,
                style={"fontSize": "clamp(0.8rem, 2.5vw, 1rem)"}
            )
        ])
    ], style={
        "width": "90%",
        "maxWidth": "500px",
        "margin": "0 auto 20px auto",
        "padding": "15px",
        "backgroundColor": "#f8f9fa",
        "borderRadius": "10px",
        "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
    }),

    # Map container with responsive height
    html.Div([
        dcc.Graph(
            id="map-graph",
            style={
                "height": "clamp(400px, 60vh, 600px)",
                "width": "100%"
            },
            config={"responsive": True}
        )
    ], style={"width": "100%", "margin": "0 auto"})
], style={
    "maxWidth": "1200px",
    "margin": "0 auto",
    "padding": "10px",
    "fontFamily": "Arial, sans-serif"
})

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
        color_continuous_scale="Reds",  # Changed to Reds
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

    # Update layout for better mobile display
    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True),
        coloraxis_colorbar=dict(
            title="Count",
            titleside="right",
            thicknessmode="pixels",
            thickness=15,
            lenmode="pixels",
            len=200
        ),
        margin=dict(t=50, b=0, l=0, r=0),
        title=dict(
            x=0.5,
            y=0.95,
            xanchor="center",
            yanchor="top",
            font=dict(size=16)
        )
    )

    return fig

# This is important for gunicorn
server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)
