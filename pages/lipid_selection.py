# Copyright (c) 2022, Colas Droin. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be found in the LICENSE file.

""" This file contains the page used to select and visualize lipids according to pre-existing 
annotations, or directly using m/z ranges."""

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
                                id="page-2-graph-lipid-selection",
                                config=basic_config
                                | {
                                    "toImageButtonOptions": {
                                        "format": "png",
                                        "filename": "brain_lipid_selection",
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
                                figure=figures.compute_grey_image_grouped(),
                            ),
                        ),
                        dmc.Group(
                            spacing=0,
                            style={
                                "left": "1%",
                                "top": "1em",
                                "flexDirection": "column",
                            },
                            className="position-absolute",
                            children=[
                                dmc.Group(
                                    spacing="xs",
                                    ta="flex-start",
                                    children=[
                                        dmc.MultiSelect(
                                            id="page-2-dropdown-lipids",
                                            data=storage.return_shelved_object(
                                                "annotations",
                                                "lipid_options",
                                                force_update=False,
                                                compute_function=data.return_lipid_options,
                                            ),
                                            searchable=True,
                                            nothingFound="No lipid found",
                                            radius="md",
                                            size="xs",
                                            placeholder="Choose up to 3 lipids",
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
                                            id="page-2-rgb-button",
                                            variant="filled",
                                            c="cyan",
                                            radius="md",
                                            size="xs",
                                            disabled=True,
                                            compact=False,
                                            loading=False,
                                        ),
                                        dmc.Button(
                                            children="Display as colormap",
                                            id="page-2-colormap-button",
                                            variant="filled",
                                            c="cyan",
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
                            id="page-2-badge-input",
                            children="Current input: " + "None",
                            className="position-absolute",
                            style={"right": "1%", "top": "1em"},
                        ),
                        dmc.Badge(
                            id="page-2-badge-lipid-1",
                            children="name-lipid-1",
                            color="red",
                            variant="filled",
                            className="d-none",
                            style={"right": "1%", "top": "4em"},
                        ),
                        dmc.Badge(
                            id="page-2-badge-lipid-2",
                            children="name-lipid-2",
                            color="teal",
                            variant="filled",
                            className="d-none",
                            style={"right": "1%", "top": "6em"},
                        ),
                        dmc.Badge(
                            id="page-2-badge-lipid-3",
                            children="name-lipid-3",
                            color="blue",
                            variant="filled",
                            className="d-none",
                            style={"right": "1%", "top": "8em"},
                        ),
                        dmc.Group(
                            align="right",
                            style={
                                "right": "1%",
                                "bottom": "4rem",
                                "flexDirection": "column",
                            },
                            className="position-absolute",
                            spacing=0,
                            children=[
                                dmc.Button(
                                    children="Download data",
                                    id="page-2-download-data-button",
                                    variant="filled",
                                    disabled=False,
                                    c="cyan",
                                    radius="md",
                                    size="xs",
                                    compact=False,
                                    loading=False,
                                    className="mt-1",
                                ),
                                dmc.Button(
                                    children="Download image",
                                    id="page-2-download-image-button",
                                    variant="filled",
                                    disabled=False,
                                    c="cyan",
                                    radius="md",
                                    size="xs",
                                    compact=False,
                                    loading=False,
                                    className="mt-1",
                                ),
                            ],
                        ),
                        dcc.Download(id="page-2-download-data"),
                    ],
                ),
                html.Div(
                    children=[
                        dbc.Offcanvas(
                            id="page-2-drawer-graph-section",
                            backdrop=False,
                            placement="end",
                            style={
                                "width": "calc(100% - 6rem)",
                                "top": "10%",
                                "height": "80%",
                                "background-color": "#1d1c1f",
                            },
                            children=[
                                dmc.Button(
                                    children="Close panel",
                                    id="page-2-close-drawer-graph-section",
                                    variant="filled",
                                    disabled=False,
                                    c="red",
                                    radius="md",
                                    size="xs",
                                    compact=False,
                                    loading=False,
                                    style={
                                        "position": "absolute",
                                        "top": "0.7rem",
                                        "right": "1rem",
                                    },
                                    className="w-25",
                                ),
                                dbc.Spinner(
                                    color="info",
                                    spinner_style={
                                        "margin-top": "40%",
                                        "width": "3rem",
                                        "height": "3rem",
                                    },
                                    children=dcc.Graph(
                                        id="page-2-graph-lipid-selection-drawer",
                                        config=basic_config,
                                        style={
                                            "width": "95%",
                                            "height": "95%",
                                            "position": "absolute",
                                            "left": "0",
                                            "top": "0",
                                            "background-color": "#1d1c1f",
                                        },
                                        figure=figures.compute_grey_image_per_slice(
                                            slice_index=slice_index
                                        ),
                                    ),
                                ),
                            ],
                        ),
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
    Output("page-2-graph-lipid-selection", "figure"),
    Output("page-2-badge-input", "children"),
    Input("page-2-badge-lipid-1", "children"),
    Input("page-2-badge-lipid-2", "children"),
    Input("page-2-badge-lipid-3", "children"),
    Input("page-2-rgb-button", "n_clicks"),
    Input("page-2-colormap-button", "n_clicks"),
    State("page-2-badge-input", "children"),
    prevent_initial_call=True,
)
def page_2_plot_graph_heatmap_selection(
    header_1,
    header_2,
    header_3,
    n_clicks_button_rgb,
    n_clicks_button_colormap,
    graph_input,
):
    """This callback plots the heatmap of the selected lipid(s)."""

    logging.info("Entering function to plot heatmap or RGB depending on lipid selection")

    # Find out which input triggered the function
    id_input = dash.callback_context.triggered[0]["prop_id"].split(".")[0]

    # If a lipid selection has been done
    if (
        id_input == "page-2-badge-lipid-1"
        or id_input == "page-2-badge-lipid-2"
        or id_input == "page-2-badge-lipid-3"
        or id_input == "page-2-rgb-button"
        or id_input == "page-2-colormap-button"
    ):  
        l_lipid_names = [header_1, header_2, header_3]

        if l_lipid_names == ["", "", ""]:
            return (
                figures.compute_grey_image_grouped(),
                "Current input: " + "None",
            )

        if (
            id_input == "page-2-badge-lipid-1"
            or id_input == "page-2-badge-lipid-2"
            or id_input == "page-2-badge-lipid-3"
        ):
            
            if (
                graph_input == "Current input: " + "Lipid selection colormap"
            ):
                return (
                    figures.compute_heatmap_grouped(
                        l_lipid_names=l_lipid_names
                    ),
                    "Current input: " + "Lipid selection colormap",
                )
            
            else:
                return (
                    figures.compute_rgb_image_grouped(
                        l_lipid_names=l_lipid_names
                    ),
                    "Current input: " + "Lipid selection RGB",
                )

        # Check if the current plot must be a heatmap
        elif (
            id_input == "page-2-colormap-button"
        ):
            return (
                figures.compute_heatmap_grouped(
                    l_lipid_names=l_lipid_names
                ),
                "Current input: " + "Lipid selection colormap",
            )

        # Or if the current plot must be an RGB image
        elif (
            id_input == "page-2-rgb-button"
        ):
            return (
                figures.compute_rgb_image_grouped(
                    l_lipid_names=l_lipid_names
                ),
                "Current input: " + "Lipid selection RGB",
            )

        # Plot grey image by default
        else:
            logging.info("Right before calling the graphing function")
            return (
                figures.compute_grey_image_grouped(),
                "Current input: " + "None",
            )

    # If no trigger, the page has just been loaded, so load new figure with default parameters
    return dash.no_update

@app.callback(
    Output("page-2-badge-lipid-1", "className"),
    Output("page-2-badge-lipid-2", "className"),
    Output("page-2-badge-lipid-3", "className"),
    Output("page-2-badge-lipid-1", "children"),
    Output("page-2-badge-lipid-2", "children"),
    Output("page-2-badge-lipid-3", "children"),
    Input("page-2-dropdown-lipids", "value"),
    Input("page-2-badge-lipid-1", "className"),
    Input("page-2-badge-lipid-2", "className"),
    Input("page-2-badge-lipid-3", "className"),
    State("page-2-badge-lipid-1", "children"),
    State("page-2-badge-lipid-2", "children"),
    State("page-2-badge-lipid-3", "children"),
)
def page_2_add_toast_selection(
    l_lipid_names,
    class_name_badge_1,
    class_name_badge_2,
    class_name_badge_3,
    header_1,
    header_2,
    header_3,
):
    """This callback adds the selected lipid to the selection."""

    logging.info("Entering function to update lipid data")

    # Find out which input triggered the function
    id_input = dash.callback_context.triggered[0]["prop_id"].split(".")[0]

    # if page-2-dropdown-lipids is called while there's no lipid name defined, it means the page
    # just got loaded
    if len(id_input) == 0 or (id_input == "page-2-dropdown-lipids" and l_lipid_names is None):
        return "d-none", "d-none", "d-none", "", "", ""
    
    # Get the current lipid selection
    selected_lipids = [header for header in [header_1, header_2, header_3] if header != ""]

    # If one or several lipids have been deleted
    if l_lipid_names is not None:
        if len(l_lipid_names) < len(selected_lipids):
            logging.info("One or several lipids have been deleter. Cleaning lipid badges now.")
            for idx_header, header in enumerate([header_1, header_2, header_3]):
                found = False
                for lipid_name in l_lipid_names:
                    if lipid_name == header:
                        found = True
                if not found:
                    if idx_header == 0:
                        header_1 = ""
                        class_name_badge_1 = "d-none"
                    if idx_header == 1:
                        header_2 = ""
                        class_name_badge_2 = "d-none"
                    if idx_header == 2:
                        header_3 = ""
                        class_name_badge_3 = "d-none"

            return (
                class_name_badge_1,
                class_name_badge_2,
                class_name_badge_3,
                header_1,
                header_2,
                header_3,
            )

    # Otherwise, update selection or add lipid
    if id_input == "page-2-dropdown-lipids" and l_lipid_names is not None:
        # Get the lipid name
        lipid_name = l_lipid_names[-1]

        change_made = True

        # Check first slot available
        if class_name_badge_1 == "d-none":
            header_1 = lipid_name
            class_name_badge_1 = "position-absolute"
        elif class_name_badge_2 == "d-none":
            header_2 = lipid_name
            class_name_badge_2 = "position-absolute"
        elif class_name_badge_3 == "d-none":
            header_3 = lipid_name
            class_name_badge_3 = "position-absolute"
        else:
            logging.warning("More than 3 lipids have been selected")
            return dash.no_update

        if change_made:
            logging.info(
                "Changes have been made to the lipid selection or indexation,"
                + " propagating callback."
            )
            return (
                class_name_badge_1,
                class_name_badge_2,
                class_name_badge_3,
                header_1,
                header_2,
                header_3,
            )
        else:
            return dash.no_update

    return dash.no_update

@app.callback(
    Output("page-2-rgb-button", "disabled"),
    Output("page-2-colormap-button", "disabled"),
    Input("page-2-badge-lipid-1", "children"),
    Input("page-2-badge-lipid-2", "children"),
    Input("page-2-badge-lipid-3", "children"),
)
def page_2_active_color_buttons(header_1, header_2, header_3):
    """This callback is used to toggle on/off the display rgb and colormap buttons."""

    logging.info("Entering function to toggle on/off the display rgb and colormap buttons")

    logging.info("Lipid indexes are: " + str(header_1) + " " + str(header_2) + " " + str(header_3))

    # Get the current lipid selection
    l_lipids_indexes = [x for x in [header_1, header_2, header_3] if x is not None and x != ""]

    # If lipids has been selected from the dropdown, activate button
    if len(l_lipids_indexes) == 1:
        return False, False
    elif len(l_lipids_indexes) > 1:
        return False, True
    else:
        return True, True

@app.callback(
    Output("page-2-drawer-graph-section", "is_open"),
    Output("page-2-main-slider-local", "data"),
    Input('page-2-graph-lipid-selection', 'clickData'),
    Input("page-2-close-drawer-graph-section", "n_clicks"),
    Input("page-2-main-slider-remote", "data"),
    [State("page-2-drawer-graph-section", "is_open")],
)
def toggle_offcanvas(clickData, n2, slice_index, is_open):
    """This callback is used to open the drawer containing the lipid expression analysis of the
    selected region."""

    input_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]

    if input_id == "page-2-main-slider-remote":
        return is_open, slice_index

    if clickData is not None:
        # Click data contains information about where the click occurred
        point = clickData['points'][0]
        trace_index = point['curveNumber']  # This corresponds to the subplot number
        slice_index = trace_index + 1
        logging.info(f"Clicked on subplot {slice_index}")
        return not is_open, slice_index
    elif n2:
        return not is_open, slice_index
    return is_open, slice_index

@app.callback(
    Output("page-2-graph-lipid-selection-drawer", "figure"),
    Input("page-2-main-slider-local", "data"),
    Input("page-2-badge-lipid-1", "children"),
    Input("page-2-badge-lipid-2", "children"),
    Input("page-2-badge-lipid-3", "children"),
    Input("page-2-rgb-button", "n_clicks"),
    Input("page-2-colormap-button", "n_clicks"),
    State("page-2-badge-input", "children"),
    [State("page-2-drawer-graph-section", "is_open")],
    prevent_initial_call=True,
)
def page_2_plot_graph_heatmap_selection_drawer(
    slice_index,
    header_1,
    header_2,
    header_3,
    n_clicks_button_rgb,
    n_clicks_button_colormap,
    graph_input,
    is_open,
):
    """This callback plots the heatmap of the selected lipid(s) in the drawer."""

    if not is_open:
        return dash.no_update

    logging.info("Entering function to plot heatmap or RGB depending on lipid selection")

    # Find out which input triggered the function
    id_input = dash.callback_context.triggered[0]["prop_id"].split(".")[0]

    # If a lipid selection has been done
    if (
        id_input == "page-2-badge-lipid-1"
        or id_input == "page-2-badge-lipid-2"
        or id_input == "page-2-badge-lipid-3"
        or id_input == "page-2-rgb-button"
        or id_input == "page-2-colormap-button"
        or (
            (id_input == "page-2-main-slider-local")
            and (
                graph_input == "Current input: " + "Lipid selection colormap"
                or graph_input == "Current input: " + "Lipid selection RGB"
                or graph_input == "Current input: " + "None"
            )
        )
    ):  
        l_lipid_names = [header_1, header_2, header_3]

        if l_lipid_names == ["", "", ""]:
            return figures.compute_grey_image_per_slice(slice_index=slice_index)

        if (
            id_input == "page-2-badge-lipid-1"
            or id_input == "page-2-badge-lipid-2"
            or id_input == "page-2-badge-lipid-3"
        ):
            
            if (
                graph_input == "Current input: " + "Lipid selection colormap"
            ):
                return figures.compute_heatmap_per_lipid_selection(
                    slice_index,
                    l_lipid_names=l_lipid_names
                    )
            
            else:
                return figures.compute_rgb_image_per_lipid_selection(
                    slice_index,
                    l_lipid_names=l_lipid_names
                    )

        # Check if the current plot must be a heatmap
        elif (
            id_input == "page-2-colormap-button"
            or (
                id_input == "page-2-main-slider-local"
                and graph_input == "Current input: " + "Lipid selection colormap"
            )
        ):
            return figures.compute_heatmap_per_lipid_selection(
                slice_index,
                l_lipid_names=l_lipid_names
                )

        # Or if the current plot must be an RGB image
        elif (
            id_input == "page-2-rgb-button"
            or (
                id_input == "page-2-main-slider-local"
                and graph_input == "Current input: " + "Lipid selection RGB"
            )
        ):
            return figures.compute_rgb_image_per_lipid_selection(
                slice_index,
                l_lipid_names=l_lipid_names
                )

        # Plot grey image by default
        else:
            logging.info("Right before calling the graphing function")
            return figures.compute_grey_image_per_slice(slice_index=slice_index),

    # If no trigger, the page has just been loaded, so load new figure with default parameters
    return dash.no_update
