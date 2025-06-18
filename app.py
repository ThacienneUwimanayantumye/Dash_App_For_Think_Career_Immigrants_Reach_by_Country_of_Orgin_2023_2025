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
    "Africa": [
        "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cabo Verde",
        "Cameroon", "Central African Republic", "Chad", "Comoros", "Congo (Brazzaville)",
        "Congo (Kinshasa)", "Côte d'Ivoire", "Djibouti", "Egypt", "Equatorial Guinea",
        "Eritrea", "Eswatini", "Ethiopia", "Gabon", "Gambia", "Ghana", "Guinea",
        "Guinea-Bissau", "Kenya", "Lesotho", "Liberia", "Libya", "Madagascar", "Malawi",
        "Mali", "Mauritania", "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger",
        "Nigeria", "Rwanda", "São Tomé and Príncipe", "Senegal", "Seychelles", "Sierra Leone",
        "Somalia", "South Africa", "South Sudan", "Sudan", "Tanzania", "Togo", "Tunisia",
        "Uganda", "Zambia", "Zimbabwe"
    ],
    "Asia": [
        "Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh", "Bhutan", "Brunei",
        "Cambodia", "China", "Cyprus", "Georgia", "India", "Indonesia", "Iran", "Iraq",
        "Israel", "Japan", "Jordan", "Kazakhstan", "Kuwait", "Kyrgyzstan", "Laos", "Lebanon",
        "Malaysia", "Maldives", "Mongolia", "Myanmar", "Nepal", "North Korea", "Oman",
        "Pakistan", "Palestine", "Philippines", "Qatar", "Saudi Arabia", "Singapore",
        "South Korea", "Sri Lanka", "Syria", "Tajikistan", "Thailand", "Timor-Leste",
        "Turkey", "Turkmenistan", "United Arab Emirates", "Uzbekistan", "Vietnam", "Yemen"
    ],
    "Europe": [
        "Albania", "Andorra", "Armenia", "Austria", "Azerbaijan", "Belarus", "Belgium",
        "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus", "Czech Republic",
        "Denmark", "Estonia", "Finland", "France", "Georgia", "Germany", "Greece", "Hungary",
        "Iceland", "Ireland", "Italy", "Kazakhstan", "Kosovo", "Latvia", "Liechtenstein",
        "Lithuania", "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro",
        "Netherlands", "North Macedonia", "Norway", "Poland", "Portugal", "Romania",
        "Russia", "San Marino", "Serbia", "Slovakia", "Slovenia", "Spain", "Sweden",
        "Switzerland", "Ukraine", "United Kingdom", "Vatican City"
    ],
    "North America": [
        "Antigua and Barbuda", "Bahamas", "Barbados", "Belize", "Canada", "Costa Rica",
        "Cuba", "Dominica", "Dominican Republic", "El Salvador", "Grenada", "Guatemala",
        "Haiti", "Honduras", "Jamaica", "Mexico", "Nicaragua", "Panama", "Saint Kitts and Nevis",
        "Saint Lucia", "Saint Vincent and the Grenadines", "Trinidad and Tobago",
        "United States"
    ],
    "South America": [
        "Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador", "Guyana", "Paraguay",
        "Peru", "Suriname", "Uruguay", "Venezuela"
    ],
    "Oceania": [
        "Australia", "Fiji", "Kiribati", "Marshall Islands", "Micronesia", "Nauru",
        "New Zealand", "Palau", "Papua New Guinea", "Samoa", "Solomon Islands", "Tonga",
        "Tuvalu", "Vanuatu"
    ],
    "Antarctica": []
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
