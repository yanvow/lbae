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

    page = html.Div(
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
                    "display": "flex",
                    "justify-content": "center",
                    "align-items": "center",
                    "height": "100%",
                },
                children=[
                    html.H1(
                        "Hello World",
                        style={"color": "white"}
                    ),
                ],
            ),
            html.Div(
                children=[
                    dbc.Offcanvas(
                        id="sidebar",
                        backdrop=True,
                        placement="start",
                        style={"width": "6rem", "background-color": "#343a40"},
                        children=[
                            # Add your sidebar content here if needed
                        ],
                    ),
                ],
            ),
        ],
    )

    return page



# ==================================================================================================
# --- Callbacks
# ==================================================================================================


