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

def return_layout(basic_config, slice_index):

    lipizones_options = storage.return_shelved_object(
        "annotations",
        "lipizones_options",
        force_update=False,
        compute_function=data.return_lipizones_options,
    )

    page = html.Div(
        style={
            "display": "flex",
            "height": "90vh",
            "background-color": "#1d1c1f",
        },
        children=[
            html.Div(
                style={
                    "width": "20%",
                    "overflow-y": "auto",
                    "background-color": "#2d2d2d",
                    "padding": "10px",
                },
                children=[
                    dmc.Checkbox(
                        id="check-all",
                        label="Check All",
                        checked=False,
                        style={"margin-bottom": "10px"},
                    ),
                    dmc.CheckboxGroup(
                        id="checkbox-group",
                        orientation="vertical",
                        offset="md",
                        mb=10,
                        children=[
                            dmc.Checkbox(label=lipizone, value=lipizone) for lipizone in lipizones_options
                        ],
                        value=[],
                    ),
                ],
            ),
            html.Div(
                style={
                    "flex-grow": 1,
                    "padding": "10px",
                },
                children=[
                    dbc.Spinner(
                        color="info",
                        spinner_style={
                            "margin-top": "40%",
                            "width": "3rem",
                            "height": "3rem",
                        },
                        children=dcc.Graph(
                            id="page-6-graph-lipizones",
                            responsive=True,
                            config=basic_config 
                            | {
                                "toImageButtonOptions": {
                                    "format": "png",
                                    "filename": "brain_lipizones",
                                    "scale": 2,
                                }
                            },
                            style={
                                "width": "100%",
                                "height": "100%",
                            },
                            figure=figures.lipizones_figure([], slice_index),
                        ),
                    ),
                ],
            ),
        ],
    )

    return page

# ==================================================================================================
# --- Callbacks
# ==================================================================================================

@app.callback(
    Output("checkbox-group", "value"),
    Input("check-all", "checked"),
)
def check_all_boxes(checked):
    if checked:
        lipizones_options = storage.return_shelved_object(
            "annotations",
            "lipizones_options",
            force_update=False,
            compute_function=data.return_lipizones_options,
        )
        return lipizones_options
    return []

@app.callback(
    Output("page-6-graph-lipizones", "figure"),
    Input("main-slider", "data"),
    Input("checkbox-group", "value"),
)
def update_figure(
    slice_index,
    selected_lipizones,
    ):
    return figures.lipizones_figure(selected_lipizones, slice_index)

