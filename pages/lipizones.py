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

    page = (
        html.Div(
            style={
                "position": "absolute",
                "top": "0px",
                "right": "0px",
                "bottom": "0px",
                "left": "6rem",
                "background-color": "#1d1c1f",
            },
            children=[
                html.Div(
                    className="fixed-aspect-ratio",
                    style={
                        "background-color": "#1d1c1f",
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
                                config=basic_config
                                | {
                                    "toImageButtonOptions": {
                                        "format": "png",
                                        "filename": "brain_lipizones",
                                        "scale": 2,
                                    }
                                }
                                | {"staticPlot": False},
                                style={
                                    "width": "95%",
                                    "height": "95%",
                                    "position": "absolute",
                                    "left": "0",
                                    "top": "0",
                                    "background-color": "#1d1c1f",
                                },
                                figure=figures.compute_heatmap_per_mz(
                                    slice_index,
                                    800,
                                    802,
                                    cache_flask=cache_flask,
                                ),
                            ),
                        ),
                        dmc.Group(
                            direction="column",
                            spacing=0,
                            style={
                                "left": "1%",
                                "top": "1em",
                            },
                            class_name="position-absolute",
                            children=[
                                dmc.Group(
                                    spacing="xs",
                                    align="flex-start",
                                    children=[
                                        dmc.MultiSelect(
                                            id="page-6-dropdown-lipizones",
                                            data=storage.return_shelved_object(
                                                "annotations",
                                                "lipizones_options",
                                                force_update=False,
                                                compute_function=data.return_lipizones_options,
                                            ),
                                            searchable=True,
                                            nothingFound="No lipizones found",
                                            radius="md",
                                            size="xs",
                                            placeholder="Choose up to 3 lipizones",
                                            clearable=False,
                                            maxSelectedValues=3,
                                            transitionDuration=150,
                                            transition="pop-top-left",
                                            transitionTimingFunction="ease",
                                            style={
                                                "width": "20em",
                                            },
                                        ),
                                        dmc.Button(
                                            children="Display as RGB",
                                            id="page-6-rgb-button",
                                            variant="filled",
                                            color="cyan",
                                            radius="md",
                                            size="xs",
                                            disabled=True,
                                            compact=False,
                                            loading=False,
                                        ),
                                        dmc.Button(
                                            children="Display as colormap",
                                            id="page-6-colormap-button",
                                            variant="filled",
                                            color="cyan",
                                            radius="md",
                                            size="xs",
                                            disabled=True,
                                            compact=False,
                                            loading=False,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        dmc.Text(
                            id="page-6-badge-input",
                            children="Current input: " + "m/z boundaries",
                            class_name="position-absolute",
                            style={"right": "1%", "top": "1em"},
                        ),
                        dmc.Badge(
                            id="page-6-badge-lipizones-1",
                            children="name-lipizones-1",
                            color="red",
                            variant="filled",
                            class_name="d-none",
                            style={"right": "1%", "top": "4em"},
                        ),
                        dmc.Badge(
                            id="page-6-badge-lipizones-2",
                            children="name-lipizones-2",
                            color="teal",
                            variant="filled",
                            class_name="d-none",
                            style={"right": "1%", "top": "6em"},
                        ),
                        dmc.Badge(
                            id="page-6-badge-lipizones-3",
                            children="name-lipizones-3",
                            color="blue",
                            variant="filled",
                            class_name="d-none",
                            style={"right": "1%", "top": "8em"},
                        ),
                        #dmc.Group(
                        #    position="right",
                        #    direction="column",
                        #    style={
                        #        "right": "1%",
                        #        "bottom": "4rem",
                        #    },
                        #    class_name="position-absolute",
                        #    spacing=0,
                        #    children=[
                        #        dmc.Button(
                        #            children="Download image",
                        #            id="page-6-download-image-button",
                        #            variant="filled",
                        #            disabled=False,
                        #            color="cyan",
                        #            radius="md",
                        #            size="xs",
                        #            compact=False,
                        #            loading=False,
                        #            class_name="mt-1",
                        #        ),
                        #    ],
                        #),
                        #dcc.Download(id="page-6-download-data"),
                    ],
                ),
            ],
        ),
    )

    return page



# ==================================================================================================
# --- Callbacks
# ==================================================================================================


@app.callback(
   Output("page-6-graph-lipizones", "figure"),
   Input("main-slider", "data"),
   Input("page-6-badge-input", "children"),
   Input("page-6-badge-lipizones-1", "children"),
   Input("page-6-badge-lipizones-2", "children"),
   Input("page-6-badge-lipizones-3", "children"),
)
def page_6_plot_graph_heatmap_mz_selection(
   slice_index, 
   graph_input,
   lipizones_1_name,
   lipizones_2_name,
   lipizones_3_name,
):
    
    if lipizones_1_name == "" and lipizones_2_name == "" and lipizones_3_name == "":
        return figures.compute_heatmap_per_mz(slice_index, 800, 802, cache_flask=cache_flask)

    if graph_input == "Current input: " + "m/z boundaries":
        print("YANIS m/z", slice_index)
        return figures.compute_heatmap_per_mz(slice_index, 800, 802, cache_flask=cache_flask)
    elif graph_input == "Current input: " + "Lipizones selection colormap":
        ll_lipizones_names = [[lipizones_1_name], [lipizones_2_name], [lipizones_3_name]]
        print("YANIS colormap", ll_lipizones_names)
        return figures.compute_heatmap_per_lipizones_selection(slice_index, ll_lipizones_names=ll_lipizones_names)
    else:
        ll_lipizones_names = [[lipizones_1_name], [lipizones_2_name], [lipizones_3_name]]
        print("YANIS rgb", ll_lipizones_names)
        return figures.compute_rgb_image_per_lipizones_selection(slice_index, ll_lipizones_names=ll_lipizones_names)
        

@app.callback(
    Output("page-6-badge-lipizones-1", "children"),
    Output("page-6-badge-lipizones-2", "children"),
    Output("page-6-badge-lipizones-3", "children"),
    Output("page-6-badge-lipizones-1", "class_name"),
    Output("page-6-badge-lipizones-2", "class_name"),
    Output("page-6-badge-lipizones-3", "class_name"),
    Output("page-6-rgb-button", "disabled"),
    Output("page-6-colormap-button", "disabled"),
    Output("page-6-badge-input", "children"),
    Input("page-6-dropdown-lipizones", "value"),
    Input("page-6-rgb-button", "n_clicks"),
    Input("page-6-colormap-button", "n_clicks"),
)
def update_badges(selected_lipids, rgb_button, colormap_button):

    input_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]

    bagde_input = "Current input: " + "m/z boundaries"

    if input_id == "page-6-rgb-button":
        bagde_input = "Current input: " + "Lipizones selection RGB"
    elif input_id == "page-6-colormap-button":
        bagde_input = "Current input: " + "Lipizones selection colormap"

    if selected_lipids is None:
        selected_lipids = []

    badge_classes = ["d-none", "d-none", "d-none"]
    badge_texts = ["", "", ""]

    for i, lipid in enumerate(selected_lipids):
        badge_classes[i] = "position-absolute"
        badge_texts[i] = lipid

    button_disabled = True

    if len(selected_lipids) > 0:
        button_disabled = False
        if input_id == "page-6-dropdown-lipizones":
            bagde_input = "Current input: " + "Lipizones selection RGB"

    return (
        badge_texts[0], badge_texts[1], badge_texts[2], 
        badge_classes[0], badge_classes[1], badge_classes[2], 
        button_disabled, button_disabled, 
        bagde_input
        )

#clientside_callback(
#    """
#    function(n_clicks){
#        if(n_clicks > 0){
#            domtoimage.toBlob(document.getElementById('page-6-graph-lipizones'))
#                .then(function (blob) {
#                    window.saveAs(blob, 'lipizones_plot.png');
#                }
#            );
#        }
#    }
#    """,
#    Output("page-6-download-image-button", "n_clicks"),
#    Input("page-6-download-image-button", "n_clicks"),
#)
#"""This clientside callback is used to download the current heatmap."""
