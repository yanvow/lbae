# Copyright (c) 2022, Colas Droin. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

""""""

# ==================================================================================================
# --- Imports
# ==================================================================================================

# Standard modules
import dash_bootstrap_components as dbc
from dash import dcc, html, clientside_callback
import logging
import dash
import json
import pandas as pd
from dash.dependencies import Input, Output, State, ALL
import dash_mantine_components as dmc

# LBAE imports
from app import app, figures, data, storage, cache_flask

# ==================================================================================================
# --- Layout
# ==================================================================================================

# Updated Layout
def return_layout(basic_config, index):

    divisions_options = data.get_lipizones_divisions()

    page = html.Div(
        style={
            "display": "flex",
            "height": "90vh",
            "background-color": "#1d1c1f",
        },
        children=[
            html.Div(
                style={
                    "left": "1%",
                    "top": "1em",
                },
                children=[
                    dmc.Select(
                        id="division-dropdown",
                        data=[{"label": division, "value": division} for division in divisions_options],
                        placeholder="Select a Division",
                        style={"margin-bottom": "10px"},
                    ),
                ],
            ),
            html.Div(
                style={
                    "flex-grow": 1,
                    "padding": "10px",
                },
                children=[
                    dcc.Loading(
                        style={
                            "margin-top": "40%",
                            "width": "3rem",
                            "height": "3rem",
                        },
                        children=dcc.Graph(
                            id="division-graph",
                            responsive=True,
                            config=basic_config,
                            style={
                                "width": "100%",
                                "height": "100%",
                            },
                            figure=figures.division_lipizones_figure(None, index),
                        ),
                    )
                ]
            ),
        ],
    )

    return page

# ==================================================================================================
# --- Callbacks
# ==================================================================================================

# Callback for updating the graph based on the selected division
@app.callback(
    Output("division-graph", "figure"),
    [Input("division-dropdown", "value")],
    prevent_initial_call=True
)
def update_division_figure(selected_division):
    if selected_division:
        return figures.division_lipizones_figure(selected_division, index)
    return {}  # Return an empty figure if no division is selected

