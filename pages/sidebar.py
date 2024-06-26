# Copyright (c) 2022, Colas Droin. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

""" This file contains the layout for the sidebar of the app."""

# ==================================================================================================
# --- Imports
# ==================================================================================================

# Standard modules
import dash_bootstrap_components as dbc
from dash import html
import dash_mantine_components as dmc

# ==================================================================================================
# --- Layout
# ==================================================================================================

layout = html.Div(
    className="sidebar",
    children=[
        dbc.Nav(
            className="sidebar-header",
            vertical=True,
            pills=True,
            children=[
                dbc.NavLink(
                    href="/",
                    active="exact",
                    className="d-flex justify-content-center align-items-center",
                    children=[
                        html.I(id="sidebar-title", className="icon-brain fs-3 m-auto pl-1"),
                    ],
                ),
            ],
        ),
        dbc.Tooltip(
            children="Return to homepage and documentation.",
            target="sidebar-title",
            placement="right",
        ),
        # Navebar to different pages
        dmc.Center(
            style={"height": "75%"},
            children=[
                dbc.Nav(
                    vertical=True,
                    pills=True,
                    children=[
                        # Link to page 1
                        dbc.NavLink(
                            href="/load-slice",
                            active="exact",
                            children=[
                                html.I(
                                    id="sidebar-page-1",
                                    className="icon-slices fs-3",
                                    style={"margin-left": "0.2em"},
                                )
                            ],
                            className="mt-1 mb-2",
                        ),
                        dbc.Tooltip(
                            children="Choose the slice you want to discover",
                            target="sidebar-page-1",
                            placement="right",
                        ),
                        # Link to page 2
                        dbc.NavLink(
                            href="/lipid-selection",
                            active="exact",
                            children=[
                                html.I(
                                    id="sidebar-page-2",
                                    className="icon-lipid fs-5",
                                    style={"margin-left": "0.7em"},
                                )
                            ],
                            className="my-4",
                        ),
                        dbc.Tooltip(
                            children=(
                                "Analyse spectrum and brain composition by custom lipid selection"
                            ),
                            target="sidebar-page-2",
                            placement="right",
                        ),
                        # Link to page 3
                        dbc.NavLink(
                            href="/region-analysis",
                            active="exact",
                            children=[
                                html.I(
                                    id="sidebar-page-3",
                                    className="icon-chart-bar fs-5",
                                    style={"margin-left": "0.7em"},
                                )
                            ],
                            className="my-4",
                        ),
                        dbc.Tooltip(
                            children="Analyse lipid composition by brain region",
                            target="sidebar-page-3",
                            placement="right",
                        ),
                        # Link to page 4
                        dbc.NavLink(
                            href="/3D-exploration",
                            active="exact",
                            # disabled=True,
                            children=[
                                html.I(
                                    id="sidebar-page-4",
                                    className="icon-3d fs-5",
                                    style={"margin-left": "0.7em"},
                                )
                            ],
                            className="my-4",
                        ),
                        dbc.Tooltip(
                            children="Analyse brain data in 3D",
                            target="sidebar-page-4",
                            placement="right",
                        ),
                        # Link to page 5
                        dbc.NavLink(
                            href="/gene-data",
                            active="exact",
                            # disabled=True,
                            children=[
                                html.I(
                                    id="sidebar-page-5",
                                    className="icon-dna fs-5",
                                    style={"margin-left": "0.7em"},
                                )
                            ],
                            className="my-4",
                        ),
                        dbc.Tooltip(
                            children="Compare with scRNAseq data",
                            target="sidebar-page-5",
                            placement="right",
                        ),
                        # Link to page 6
                        dbc.NavLink(
                            href="/lipizones",
                            active="exact",
                            # disabled=True,
                            children=[
                                html.I(
                                    id="sidebar-page-6",
                                    className="icon-slices fs-3",
                                    style={"margin-left": "0.2em"},
                                )
                            ],
                            className="my-4",
                        ),
                        dbc.Tooltip(
                            children="Explore lipid zones",
                            target="sidebar-page-6",
                            placement="right",
                        ),
                        # Link to documentation
                        html.Div(
                            className="sidebar-bottom",
                            children=[
                                dbc.NavLink(
                                    id="sidebar-documentation",
                                    n_clicks=0,
                                    active="exact",
                                    children=[
                                        html.I(
                                            id="sidebar-documentation-inside",
                                            className="icon-library mb-3 fs-3",
                                            style={"margin-left": "0.5rem"},
                                        )
                                    ],
                                ),
                                dbc.Tooltip(
                                    children="Open documentation",
                                    target="sidebar-documentation-inside",
                                    placement="right",
                                ),
                                html.H4(
                                    id="sidebar-copyright",
                                    className="icon-cc mb-3 mt-3 fs-2",
                                    style={"color": "#dee2e6", "margin-left": "0.5rem"},
                                ),
                                dbc.Tooltip(
                                    children="Copyright EPFL 2022",
                                    target="sidebar-copyright",
                                    placement="right",
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)
