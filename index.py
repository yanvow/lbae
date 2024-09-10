# Copyright (c) 2022, Colas Droin. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

""" This module is where the app layout is created: the main container, the sidebar and the 
different pages. All the dcc.store, used to store client data across pages, are created here. It is 
also here that the URL routing is done.
"""

# ==================================================================================================
# --- Imports
# ==================================================================================================

# Standard modules
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
import uuid
import logging
import dash_mantine_components as dmc
import dash

# LBAE modules
from app import app, data, atlas
from pages import (
    sidebar,
    home,
    load_slice,
    lipid_selection,
    region_analysis,
    threeD_exploration,
    lipizones,
    lipizones2,
)
from in_app_documentation.documentation import return_documentation
from config import basic_config
from modules.tools.misc import logmem

# ==================================================================================================
# --- App layout
# ==================================================================================================


def return_main_content():
    """This function compute the elements of the app that are shared across pages, including all the
    dcc.store.

    Returns:
        (html.Div): A div containing the corresponding elements.
    """
    # List of empty lipid indexes for the dropdown of page 4, assuming brain 1 is initially selected
    empty_lipid_list = [-1 for i in data.get_slice_list(indices="brain_1")]

    # Record session id in case sessions need to be individualized
    session_id = str(uuid.uuid4())

    # Define static content
    main_content = html.Div(
        children=[
            # To handle url since multi-page app
            dcc.Location(id="url", refresh=False),
            # Record session id, useful to trigger callbacks at initialization
            dcc.Store(id="session-id", data=session_id),
            # Record the slider index
            dcc.Store(id="main-slider", data=1),
            dcc.Store(id="main-slider-client", data=1),
            dcc.Store(id="page-2-main-slider-local", data=1),
            dcc.Store(id="page-2-main-slider-remote", data=1),
            # Record the state of the range sliders for low and high resolution spectra in page 2
            dcc.Store(id="boundaries-low-resolution-mz-plot"),
            dcc.Store(id="boundaries-high-resolution-mz-plot"),
            # Record the lipids selected in page 2
            dcc.Store(id="page-2-selected-lipid-1", data=-1),
            dcc.Store(id="page-2-selected-lipid-2", data=-1),
            dcc.Store(id="page-2-selected-lipid-3", data=-1),
            dcc.Store(id="page-2-last-selected-lipids", data=[]),
            # Record the lipids selected in page 4
            dcc.Store(id="page-4-selected-lipid-1", data=empty_lipid_list),
            dcc.Store(id="page-4-selected-lipid-2", data=empty_lipid_list),
            dcc.Store(id="page-4-selected-lipid-3", data=empty_lipid_list),
            dcc.Store(id="page-4-last-selected-regions", data=[]),
            dcc.Store(id="page-4-selected-region-1", data=""),
            dcc.Store(id="page-4-selected-region-2", data=""),
            dcc.Store(id="page-4-selected-region-3", data=""),
            dcc.Store(id="page-4-last-selected-lipids", data=[]),
            # Record the shapes drawn in page 3
            dcc.Store(id="dcc-store-color-mask", data=[]),
            dcc.Store(id="dcc-store-reset", data=False),
            dcc.Store(id="dcc-store-shapes-and-masks", data=[]),
            dcc.Store(id="dcc-store-list-idx-lipids", data=[]),
            # Record the annotated paths drawn in page 3
            dcc.Store(id="page-3-dcc-store-path-heatmap"),
            dcc.Store(id="page-3-dcc-store-basic-figure", data=True),
            # Record the computed spectra drawn in page 3
            dcc.Store(id="dcc-store-list-mz-spectra", data=[]),
            # Record the lipids expressed in the region in page 3
            dcc.Store(id="page-3-dcc-store-lipids-region", data=[]),
            # Actual app layout
            html.Div(
                children=[
                    sidebar.layout,
                    html.Div(id="content"),
                    dmc.Center(
                        id="main-paper-slider",
                        style={
                            "position": "fixed",
                            "bottom": "1rem",
                            "height": "3rem",
                            "left": "7rem",
                            "right": "1rem",
                            "background-color": "rgba(0, 0, 0, 0.0)",
                        },
                        children=[
                            dmc.Text(
                                id="main-text-slider",
                                children="Rostro-caudal coordinate (mm): ",
                                className="pr-4",
                                size="sm",
                            ),
                            dmc.Slider(
                                id="main-slider-1",
                                min=data.get_slice_list(indices="brain_1")[0],
                                max=data.get_slice_list(indices="brain_1")[-1],
                                step=1,
                                marks=[
                                    {
                                        "value": slice_index,
                                        # Use x coordinate for label
                                        "label": "{:.2f}".format(
                                            atlas.l_original_coor[slice_index - 1][0, 0][0]
                                        ),
                                    }
                                    for slice_index in data.get_slice_list(indices="brain_1")[::3]
                                ],
                                size="xs",
                                value=data.get_slice_list(indices="brain_1")[0],
                                c="cyan",
                                className="mt-2 mr-5 ml-2 mb-1 w-50",
                            ),
                            dmc.Slider(
                                id="main-slider-2",
                                min=data.get_slice_list(indices="brain_2")[0],
                                max=data.get_slice_list(indices="brain_2")[-1],
                                step=1,
                                marks=[
                                    {
                                        "value": slice_index,
                                        # Use x coordinate for label
                                        "label": "{:.2f}".format(
                                            atlas.l_original_coor[slice_index - 1][0, 0][0]
                                        ),
                                    }
                                    for slice_index in data.get_slice_list(indices="brain_2")[::3]
                                ],
                                size="xs",
                                value=data.get_slice_list(indices="brain_2")[0],
                                c="cyan",
                                className="mt-2 mr-5 ml-2 mb-1 w-50 d-none",
                            ),
                            dmc.ChipGroup(
                                [
                                    dmc.Chip(
                                        "Brain 1",
                                        value="brain_1",
                                        variant="outline",
                                    ),
                                    dmc.Chip(
                                        "Brain 2",
                                        value="brain_2",
                                        variant="outline",
                                    ),
                                ],
                                id="main-brain",
                                value=["brain_1"], 
                                multiple=False, 
                                className="pl-2 pt-1",
                                c="cyan", 
                            ),
                        ],
                    ),
                    # Documentation in a bottom drawer
                    dmc.Drawer(
                        children=return_documentation(app),
                        id="documentation-offcanvas",
                        # title="LBAE documentation",
                        opened=False,
                        padding="md",
                        size="90vh",
                        style={"textAlign": "bottom"},
                    ),
                    # Spinner when switching pages
                    dbc.Spinner(
                        id="main-spinner",
                        color="light",
                        children=html.Div(id="empty-content"),
                        fullscreen=True,
                        fullscreen_style={"left": "6rem", "background-color": "#1d1c1f"},
                        spinner_style={"width": "6rem", "height": "6rem"},
                        delay_hide=100,
                    ),
                ],
            ),
        ],
    )
    return main_content


def return_validation_layout(main_content, initial_slice=1, brain="brain_1"):
    """This function compute the layout of the app, including the main container, the sidebar and
    the different pages.

    Args:
        main_content (html.Div): A div containing the elements of the app that are shared across
            pages.
        initial_slice (int): Index of the slice to be displayed at launch.

    Returns:
        (html.Div): A div containing the layout of the app.
    """
    return html.Div(
        [
            main_content,
            home.layout,
            load_slice.return_layout(basic_config, initial_slice),
            lipid_selection.return_layout(basic_config, initial_slice),
            region_analysis.return_layout(basic_config, initial_slice),
            threeD_exploration.return_layout(basic_config, initial_slice),
            lipizones.return_layout(basic_config, initial_slice),
            lipizones2.return_layout(basic_config, initial_slice),
        ]
    )


# ==================================================================================================
# --- App callbacks
# ==================================================================================================
@app.callback(
    Output("content", "children"),
    Output("empty-content", "children"),
    Input("url", "pathname"),
    State("main-slider", "data"),
    State("main-brain", "value"),
)
def render_page_content(pathname, slice_index, brain):
    """This callback is used as a URL router."""

    # Keep track of the page in the console
    if pathname is not None:
        logging.info("Page" + pathname + " has been selected" + logmem())

    # Set the content according to the current pathname
    if pathname == "/":
        page = home.layout

    elif pathname == "/load-slice":
        page = load_slice.return_layout(basic_config, slice_index)

    elif pathname == "/lipid-selection":
        page = lipid_selection.return_layout(basic_config, slice_index)

    elif pathname == "/region-analysis":
        page = region_analysis.return_layout(basic_config, slice_index)

    elif pathname == "/3D-exploration":
        page = threeD_exploration.return_layout(basic_config, slice_index)

    elif pathname == "/lipizones":
        page = lipizones.return_layout(basic_config, slice_index)

    elif pathname == "/lipizones2":
        page = lipizones2.return_layout(basic_config, slice_index)

    else:
        # If the user tries to reach a different page, return a 404 message
        page = dmc.Center(
            dmc.Alert(
                title="404: Not found",
                children=f"The pathname {pathname} was not recognised...",
                c="red",
                className="mt-5",
            ),
            className="mt-5",
        )
    return page, ""


@app.callback(
    Output("documentation-offcanvas", "opened"),
    [
        Input("sidebar-documentation", "n_clicks"),
    ],
    [State("documentation-offcanvas", "opened")],
)
def toggle_collapse(n1, is_open):
    """This callback triggers the modal windows that toggles the documentation when clicking on the
    corresponding button."""
    if n1:
        return not is_open
    return is_open


@app.callback(
    Output("main-paper-slider", "className"), Input("url", "pathname"), prevent_initial_call=False
)
def hide_slider(pathname):
    """This callback is used to hide the slider div when the user is on a page that does not need it.
    """

    # Pages in which the slider is displayed
    l_path_with_slider = [
        "/load-slice",
        "/lipid-selection",
        "/region-analysis",
        "/3D-exploration",
        "/lipizones",
        "/lipizones2",
    ]

    # Set the content according to the current pathname
    if pathname in l_path_with_slider:
        return ""

    else:
        return "d-none"


@app.callback(
    Output("main-slider-1", "style"),
    Output("main-slider-2", "style"),
    Output("main-text-slider", "style"),
    Input("url", "pathname"),
    prevent_initial_call=False,
)
def hide_slider_but_leave_brain(pathname):
    """This callback is used to hide the slider but leave brain chips when needed."""

    # Pages in which the slider is displayed
    l_path_without_slider_but_with_brain = [
        "/3D-exploration",
    ]

    # Set the content according to the current pathname
    if pathname in l_path_without_slider_but_with_brain:
        return {"visibility": "hidden"}, {"visibility": "hidden"}, {"visibility": "hidden"}

    else:
        return {}, {}, {}


@app.callback(
    Output("main-slider-1", "className"),
    Output("main-slider-2", "className"),
    Output("main-slider-1", "value"),
    Output("main-slider-2", "value"),
    Input("main-brain", "value"),
    Input("main-slider", "data"),
    State("main-slider-1", "value"),
    State("main-slider-2", "value"),
    prevent_initial_call=False,
)
def hide_useless_slider(brain, slider, value_1, value_2):
    """This callback is used to update the slider indices with the selected brain."""
    if brain == "brain_1":
        return "mt-2 mr-5 ml-2 mb-1 w-50", "mt-2 mr-5 ml-2 mb-1 w-50 d-none", slider, value_2
    elif brain == "brain_2":
        return "mt-2 mr-5 ml-2 mb-1 w-50 d-none", "mt-2 mr-5 ml-2 mb-1 w-50", value_1, slider
    else:
        return "mt-2 mr-5 ml-2 mb-1 w-50", "mt-2 mr-5 ml-2 mb-1 w-50 d-none", value_1, value_2


app.clientside_callback(
    """
    function(value_1, value_2, brain){
        if(brain == 'brain_1'){
            return value_1;
        }
        else if(brain == 'brain_2'){
            return value_2;
            }
    }
    """,
    Output("main-slider-client", "data"),
    Input("main-slider-1", "value"),
    Input("main-slider-2", "value"),
    State("main-brain", "value"),
)
"""This clientside callback is used to update the slider indices with the selected brain."""

@app.callback(
    Output("page-2-main-slider-remote", "data"),
    Input("main-slider", "data"),
    Input("page-2-main-slider-local", "data"),
)
def update_remote_main_sliders(global_brain, local_brain_2):
    """This callback is used to update the slider indices with the selected brain."""
    
    input_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]

    if input_id == "main-slider":
        return global_brain
    elif input_id == "page-2-main-slider-local":
        return local_brain_2

@app.callback(
    Output("main-slider", "data"),
    Input("main-slider-client", "data"),
    Input("page-2-main-slider-remote", "data"),
)
def update_remote_main_sliders(client_brain, remote_brain_2):
    """This callback is used to update the slider indices with the selected brain."""
    
    input_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]

    if input_id == "main-slider-client":
        return client_brain
    elif input_id == "page-2-main-slider-remote":
        return remote_brain_2
