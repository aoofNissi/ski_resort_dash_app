
from dash import Dash, dcc, html, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate
# from dash_bootstrap_templates import load_figure_template

import plotly.express as px
import pandas as pd
import numpy as np
import plotly.io as pio
from os import sys

resorts = (
    pd.read_csv("../Data/Ski Resorts/resorts.csv", encoding = "ISO-8859-1")
    # .query("Country in ['United States', 'Canada']")
    .assign(
        country_elevation_rank = lambda x: x.groupby("Country", as_index=False)["Highest point"].rank(ascending=False),
        country_price_rank = lambda x: x.groupby("Country", as_index=False)["Price"].rank(ascending=False),
        country_slope_rank = lambda x: x.groupby("Country", as_index=False)["Total slopes"].rank(ascending=False),
        country_cannon_rank = lambda x: x.groupby("Country", as_index=False)["Snow cannons"].rank(ascending=False),
    ))

continents = resorts["Continent"].unique()
countries = resorts["Country"].unique()
fields=resorts.select_dtypes(include=np.number).columns.tolist()
countriesbycontinents = resorts.groupby("Continent")["Country"].unique().apply(list).to_dict()

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

pio.templates.default = "plotly"

app.layout = html.Div([
    dcc.Tabs(id="skiitabs",
        children = [
            dcc.Tab(
                label="Density Map", value="tab1",
                children = [
                    dbc.Row([
                            dbc.Col([
                                dcc.Slider(id="priceslider",
                                    min=resorts["Price"].min(),
                                    max=150, #resorts["Price"].max(),
                                    step=25,
                                    value=150
                                ), 
                                dcc.RadioItems(id="nightskiingtoggle",
                                    options = [{"label" : "Has Night Skii", "value" : "Yes"}, 
                                               {"label" : "No Night Skii", "value" : "No"}],
                                              value="No"
                                ),
                                dcc.Checklist(id = "skiitype",
                                    options = ["Has Summer Skiing","Has Night Skiing","Has Snow Park"],
                                    value = ["Has Summer Skiing"],
                                )
                            ], width=3),
                            dbc.Col([
                                dcc.Graph(id="densitymapboxtotalslopes",
                                         style={'height': '80vh'} 
                                ),
                            ], width=9)
                        ])
                ]),
            dcc.Tab(
                label="Bar Chart", value="tab2",
                children = [
                    dbc.Row([
                        dbc.Col([
                            "Dropdowns",
                            html.H6("Continent"),
                            dcc.Dropdown(id="continentsdropdown",
                                options=continents,
                                value="Asia"
                            ),
                            html.H6("Country"),
                            dcc.Dropdown(id="countrydropdown",
                                value=""
                            ),
                            html.H6("Field"),
                            dcc.Dropdown(id="fielddropdown",
                                options=fields[3:14],
                                value=fields[3]
                            ),
                        ], width=3),
                        dbc.Col([
                            "Bar Chart",
                            dcc.Graph(id="skiiattributebarchart",
                                style={'height': '60vh', 'width': '85vh'}
                            )
                        ], width=6),
                        dbc.Col([
                            "Report Card"
                        ], width=3)
                    ])
                ]
            )
        ]
    ),
])

@app.callback(
    Output("densitymapboxtotalslopes", "figure"),
    Input("priceslider", "value"),
    Input("nightskiingtoggle", "value")
)
def skiing_hotspots(price, nightskii):
    if not price:
        raise PreventUpdate
    if not nightskii:
        raise PreventUpdate

    dashdata = resorts.query(f'Nightskiing == "{nightskii}" & Price <= {price}')

    densitymap = px.density_map(
        dashdata,
        lat="Latitude",
        lon="Longitude",
        center={'lat': 49.004087, 'lon': -103.818459},
        z="Total slopes",
        hover_name="Resort",
        radius=15,
        zoom=2.5,
        # color_continuous_scale="blues",
    )
    return  densitymap

@app.callback(
    Output("countrydropdown", "options"),
    Output("countrydropdown", "value"),
    Input("continentsdropdown", "value")
)
def countries_by_continent(continent):
    return countriesbycontinents[continent], countriesbycontinents[continent][0]


@app.callback(
    Output("skiiattributebarchart", "figure")
    ,Input("countrydropdown", "value")
    ,Input("fielddropdown", "value")
)
def draw_skii_attribute_bar_chart(country, field):
    df_barchart = (resorts
                   .query(f'Country == "{country}"')
                   .sort_values(field, ascending=False)).head(10)
    barfigure = px.bar(
        df_barchart,
        x="Resort",
        y=field
    ).update_xaxes(showticklabels=False)
    return barfigure


if __name__ == "__main__":
    app.run(debug = True)
