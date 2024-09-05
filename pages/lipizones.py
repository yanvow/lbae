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

dendrogram_bottomup = 0
dendrogram_index = 0

def return_layout(basic_config, slice_index):

    lipizones_options = get_all_lipizones()

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
                    html.Div(
                        style={
                            "display": "flex",
                            "flex-direction": "row",
                            "align-items": "center",
                        },
                        children=[
                            dmc.Button(
                                id="update-checkbox-button",
                                children="Checkbox Update",
                                color="primary",
                                style={"margin-bottom": "10px"},
                            ),
                            dmc.Button(
                                id="update-dendrogram-button",
                                children="Dendrogram Update",
                                color="primary",
                                style={"margin-bottom": "10px"},
                            ),
                        ]
                    ),
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
                    dcc.Loading(
                        style={
                                "margin-top": "40%",
                                "width": "3rem",
                                "height": "3rem",
                            },
                        children=
                            dcc.Graph(
                                id="page-6-graph-lipizones",
                                responsive=True,
                                config=basic_config,
                                style={
                                    "width": "100%",
                                    "height": "100%",
                                },
                                figure=figures.lipizones_figure([], slice_index),
                            ),
                    )
                ]
            ),
            html.Div(
                style={
                    "width": "20%",  # Adjusted width for right sidebar
                    "padding": "10px",
                    "background-color": "#2d2d2d",
                    "display": "flex",
                    "flex-direction": "row",
                    "align-items": "center",  # Centering content horizontally
                    "overflow-y": "auto"
                },
                children=[
                    dmc.Button(
                        id="back-button",
                        children="Back",
                        color="primary",
                        style={"margin-right": "10px"},
                    ),
                    html.Div(
                        style={
                            "width": "100%",
                            "display": "flex",
                            "flex-direction": "column",
                            "align-items": "center",
                        },
                        children=[
                            dmc.Button(
                            id="up-button",
                            children="Up",
                            color="primary",
                            style={"margin-bottom": "10px"},
                            ),
                            dmc.Button(
                                id="down-button",
                                children="Down",
                                color="primary",
                                style={"margin-bottom": "10px"},
                            )
                        ]
                    ),
                    html.Div(
                        style={
                            "flex-grow": "1",  # Allow the graph container to grow and fill available space
                            "display": "flex",
                            "justify-content": "center",
                            "align-items": "center",
                        },
                        children=dcc.Loading(
                            style={
                                "margin-top": "40%",
                                "width": "3rem",
                                "height": "3rem",
                            },
                            children=dcc.Graph(
                                id="page-6-dendrogram-lipizones",
                                responsive=True,
                                config=basic_config,
                                style={
                                    "width": "100%",
                                    "height": "100%",
                                },
                                figure=figures.dendrogram_lipizones(dendrogram_bottomup, dendrogram_index),
                            ),
                        )
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
        lipizones_options = get_all_lipizones()
        return lipizones_options
    return []

@app.callback(
    Output("page-6-graph-lipizones", "figure"),
    [Input("update-checkbox-button", "n_clicks"),
     Input("update-dendrogram-button", "n_clicks")],
    [State("main-slider", "data"),         # States to get values without triggering callback
     State("checkbox-group", "value")],
    prevent_initial_call=True
)
def update_figure(update_checkbox, update_dendrogram, slice_index, selected_lipizones):

    id_input = dash.callback_context.triggered[0]["prop_id"].split(".")[0]

    if id_input == "update-checkbox-button":
        logging.info("Checkbox update button clicked")
        return figures.lipizones_figure(selected_lipizones, slice_index)
    else:
        logging.info("Dendrogram update button clicked")
        selected_lipizones = data.get_lipizones_centroids(dendrogram_bottomup, dendrogram_index).index.tolist()
        return figures.lipizones_figure(selected_lipizones, slice_index)

@app.callback(
    Output("page-6-dendrogram-lipizones", "figure"),
    Output("back-button", "disabled"),
    Input("back-button", "n_clicks"),
    Input("up-button", "n_clicks"),
    Input("down-button", "n_clicks"),
    prevent_initial_call=True
)
def update_dendrogram(back, up, down):
    # Update the figure based on the button clicks
    global dendrogram_bottomup, dendrogram_index  # Ensure these are modified globally

    id_input = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    
    if id_input == "up-button":
        logging.info("Up button clicked")
        dendrogram_bottomup += 1
        dendrogram_index = 1 if dendrogram_index == 0 else dendrogram_index * 2 - 1
        return figures.dendrogram_lipizones(dendrogram_bottomup, dendrogram_index), False
    elif id_input == "down-button":
        logging.info("Down button clicked")
        dendrogram_bottomup += 1
        dendrogram_index = 2 if dendrogram_index == 0 else dendrogram_index * 2 
        return figures.dendrogram_lipizones(dendrogram_bottomup, dendrogram_index), False
    else:
        logging.info("Back button clicked")
        dendrogram_bottomup -= 1
        dendrogram_index = (dendrogram_index + 1) // 2
        if dendrogram_bottomup == 0:
            dendrogram_index = 0
            return figures.dendrogram_lipizones(dendrogram_bottomup, dendrogram_index), True
        return figures.dendrogram_lipizones(dendrogram_bottomup, dendrogram_index), False

def get_all_lipizones():
    return storage.return_shelved_object(
        "annotations",
        "lipizones_options",
        force_update=False,
        compute_function=data.get_lipizone_names,
    )
