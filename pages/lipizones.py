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
                                id="page-2-graph-lipizones",
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
                                            id="page-2-dropdown-lipizones",
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
                                            id="page-2-rgb-button",
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
                                            id="page-2-colormap-button",
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
                            id="page-2-badge-input",
                            children="Current input: " + "m/z boundaries",
                            class_name="position-absolute",
                            style={"right": "1%", "top": "1em"},
                        ),
                        dmc.Badge(
                            id="page-2-badge-lipizones-1",
                            children="name-lipizones-1",
                            color="red",
                            variant="filled",
                            class_name="d-none",
                            style={"right": "1%", "top": "4em"},
                        ),
                        dmc.Badge(
                            id="page-2-badge-lipizones-2",
                            children="name-lipizones-2",
                            color="teal",
                            variant="filled",
                            class_name="d-none",
                            style={"right": "1%", "top": "6em"},
                        ),
                        dmc.Badge(
                            id="page-2-badge-lipizones-3",
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
                        #            id="page-2-download-image-button",
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
                        #dcc.Download(id="page-2-download-data"),
                    ],
                ),
            ],
        ),
    )

    return page



# ==================================================================================================
# --- Callbacks
# ==================================================================================================


#@app.callback(
#    Output("page-2-graph-lipizones", "figure"),
#    Output("page-2-badge-input", "children"),
#    Input("main-slider", "data"),
#    Input("page-2-selected-lipizones-1", "data"),
#    Input("page-2-selected-lipizones-2", "data"),
#    Input("page-2-selected-lipizones-3", "data"),
#    State("page-2-lower-bound", "value"),
#    State("page-2-upper-bound", "value"),
#    State("page-2-badge-input", "children"),
#)
#def page_2_plot_graph_heatmap_mz_selection(
#    slice_index, 
#    lipizones_1_index,
#    lipizones_2_index,
#    lipizones_3_index,
#    lb,
#    hb,
#    graph_input
#):
#
#    logging.info("Entering function to plot heatmap or RGB depending on lipizones selection")
#
#    # Find out which input triggered the function
#    id_input = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
#
#    # If a lipizones selection has been done
#    if (
#        id_input == "page-2-selected-lipizones-1"
#        or id_input == "page-2-selected-lipizones-2"
#        or id_input == "page-2-selected-lipizones-3"
#        or id_input == "page-2-rgb-button"
#        or id_input == "page-2-colormap-button"
#        or (
#            (id_input == "main-slider" or id_input == "page-2-toggle-apply-transform")
#            and (
#                graph_input == "Current input: " + "Lipizones selection colormap"
#                or graph_input == "Current input: " + "Lipizones selection RGB"
#            )
#        )
#    ):
#        if lipizones_1_index >= 0 or lipizones_2_index >= 0 or lipizones_3_index >= 0:
#             
#            ll_lipizones_names = [
#                [
#                    "level"
#                    + "_"
#                    + data.get_annotations().iloc[index]["level"]
#                    + "_"
#                    + data.get_annotations().iloc[index]["value"]
#                ]
#                if index != -1
#                else None
#                for index in [lipizones_1_index, lipizones_2_index, lipizones_3_index]
#            ]
#             
#            # Check if the current plot must be a heatmap
#            if (
#                id_input == "page-2-colormap-button"
#                or (
#                    id_input == "main-slider"
#                    and graph_input == "Current input: " + "Lipizones selection colormap"
#                )
#                or (
#                    id_input == "page-2-toggle-apply-transform"
#                    and graph_input == "Current input: " + "Lipizones selection colormap"
#                )
#            ):
#                return (
#                    figures.compute_heatmap_per_lipizones_selection(
#                        slice_index,
#                        ll_lipizones_names=ll_lipizones_names,
#                        cache_flask=cache_flask,
#                    ),
#                    "Current input: " + "Lipizones selection colormap",
#                )
#
#            # Or if the current plot must be an RGB image
#            elif (
#                id_input == "page-2-rgb-button"
#                or (
#                    id_input == "main-slider"
#                    and graph_input == "Current input: " + "Lipizones selection RGB"
#                )
#                or (
#                    id_input == "page-2-toggle-apply-transform"
#                    and graph_input == "Current input: " + "Lipizones selection RGB"
#                )
#            ):
#                return (
#                    figures.compute_rgb_image_per_lipizones_selection(
#                        slice_index,
#                        ll_lipizones_names=ll_lipizones_names,
#                        cache_flask=cache_flask,
#                    ),
#                    "Current input: " + "Lipizones selection RGB",
#                )
#            
#            # Plot RBG By default
#            else:
#                logging.info("Right before calling the graphing function")
#                return (
#                    figures.compute_rgb_image_per_lipizones_selection(
#                        slice_index,
#                        ll_lipizones_names=ll_lipizones_names,
#                        cache_flask=cache_flask,
#                    ),
#                    "Current input: " + "Lipizones selection RGB",
#                )
#        else:
#            # No lipizones has been selected, return image from boundaries
#            return (
#                    figures.compute_heatmap_per_mz(
#                        slice_index, 
#                        lb, 
#                        hb, 
#                        cache_flask=cache_flask
#                    ),
#                    "Current input: " + "m/z boundaries",
#                )  
#         
#    # If no trigger, the page has just been loaded, so load new figure with default parameters
#    else:
#        return dash.no_update
#
#@app.callback(
#    Output("page-2-badge-lipizones-1", "children"),
#    Output("page-2-badge-lipizones-2", "children"),
#    Output("page-2-badge-lipizones-3", "children"),
#    Output("page-2-selected-lipizones-1", "data"),
#    Output("page-2-selected-lipizones-2", "data"),
#    Output("page-2-selected-lipizones-3", "data"),
#    Output("page-2-badge-lipizones-1", "class_name"),
#    Output("page-2-badge-lipizones-2", "class_name"),
#    Output("page-2-badge-lipizones-3", "class_name"),
#    Input("page-2-dropdown-lipizones", "value"),
#    Input("page-2-badge-lipizones-1", "class_name"),
#    Input("page-2-badge-lipizones-2", "class_name"),
#    Input("page-2-badge-lipizones-3", "class_name"),
#    Input("main-slider", "data"),
#    State("page-2-selected-lipizones-1", "data"),
#    State("page-2-selected-lipizones-2", "data"),
#    State("page-2-selected-lipizones-3", "data"),
#    State("page-2-badge-lipizones-1", "children"),
#    State("page-2-badge-lipizones-2", "children"),
#    State("page-2-badge-lipizones-3", "children"),
#)
#def page_2_add_toast_selection(
#    l_lipizones_names,
#    class_name_badge_1,
#    class_name_badge_2,
#    class_name_badge_3,
#    slice_index,
#    lipizones_1_index,
#    lipizones_2_index,
#    lipizones_3_index,
#    header_1,
#    header_2,
#    header_3,
#):
#    """This callback adds the selected lipizones to the selection."""
#
#    logging.info("Entering function to update lipizones data")
#
#    # Find out which input triggered the function
#    id_input = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
#
#    # if page-2-dropdown-lipizones is called while there's no lipizones name defined, it means the page
#    # just got loaded
#    if len(id_input) == 0 or (id_input == "page-2-dropdown-lipizones" and l_lipizones_names is None):
#        return "", "", "", -1, -1, -1, "d-none", "d-none", "d-none"  # , None
#
#    # If one or several lipizones have been deleted
#    if l_lipizones_names is not None:
#        if len(l_lipizones_names) < len(
#            [x for x in [lipizones_1_index, lipizones_2_index, lipizones_3_index] if x != -1]
#        ):
#            logging.info("One or several lipizones have been deleter. Cleaning lipizones badges now.")
#            for idx_header, header in enumerate([header_1, header_2, header_3]):
#                found = False
#                for lipizones_name in l_lipizones_names:
#                    if lipizones_name == header:
#                        found = True
#                if not found:
#                    if idx_header == 0:
#                        header_1 = ""
#                        lipizones_1_index = -1
#                        class_name_badge_1 = "d-none"
#                    if idx_header == 1:
#                        header_2 = ""
#                        lipizones_2_index = -1
#                        class_name_badge_2 = "d-none"
#                    if idx_header == 2:
#                        header_3 = ""
#                        lipizones_3_index = -1
#                        class_name_badge_3 = "d-none"
#
#            return (
#                header_1,
#                header_2,
#                header_3,
#                lipizones_1_index,
#                lipizones_2_index,
#                lipizones_3_index,
#                class_name_badge_1,
#                class_name_badge_2,
#                class_name_badge_3,
#            )
#    # Otherwise, update selection or add lipizones
#    if (
#        id_input == "page-2-dropdown-lipizones" and l_lipizones_names is not None
#    ) or id_input == "main-slider":
#
#        # If a new slice has been selected
#        if id_input == "main-slider":
#
#            # for each lipizones, get lipizones name, structure and cation
#            for header in [header_1, header_2, header_3]:
#
#                if len(header) > 2:
#                    _, level, lipotype = header.split(" ")
#
#                    # Find lipizones location
#                    l_lipizones_loc_temp = (
#                        data.get_lipizones()
#                        .index[
#                            (data.get_lipizones()["level"] == level)
#                            & (data.get_lipizones()["lipotype"] == lipotype)
#                        ]
#                        .tolist()
#                    )
#                    l_lipizones_loc = [
#                        l_lipizones_loc_temp[i]
#                        for i, x in enumerate(
#                            data.get_lipizones().iloc[l_lipizones_loc_temp]["slice"] == slice_index
#                        )
#                        if x
#                    ]
#
#                    # Fill list with first annotation that exists if it can't find one for the
#                    # current slice
#                    if len(l_lipizones_loc) == 0:
#                        l_lipizones_loc = l_lipizones_loc_temp[:1]
#
#                    # Record location and lipizones name
#                    lipizones_index = l_lipizones_loc[0]
#
#                    # If lipizones has already been selected before, replace the index
#                    if header_1 == header:
#                        lipizones_1_index = lipizones_index
#                    elif header_2 == header:
#                        lipizones_2_index = lipizones_index
#                    elif header_3 == header:
#                        lipizones_3_index = lipizones_index
#
#            logging.info("Returning updated lipizones data")
#            return (
#                header_1,
#                header_2,
#                header_3,
#                lipizones_1_index,
#                lipizones_2_index,
#                lipizones_3_index,
#                class_name_badge_1,
#                class_name_badge_2,
#                class_name_badge_3,
#            )
#
#        # If lipizones have been added from dropdown menu
#        elif id_input == "page-2-dropdown-lipizones":
#            # Get the lipizones name and structure
#            _, level, lipotype = l_lipizones_names[-1].split(" ")
#
#            # Find lipizones location
#            l_lipizones_loc = (
#                data.get_lipizones()
#                .index[
#                    (data.get_lipizones()["level"] == level)
#                    & (data.get_lipizones()["slice"] == slice_index)
#                    & (data.get_lipizones()["lipotype"] == lipotype)
#                ]
#                .tolist()
#            )
#
#            # If several lipizones correspond to the selection, we have a problem...
#            if len(l_lipizones_loc) > 1:
#                logging.warning("More than one lipizones corresponds to the selection")
#                l_lipizones_loc = [l_lipizones_loc[-1]]
#
#            if len(l_lipizones_loc) < 1:
#                logging.warning("No lipizones annotation exist. Taking another slice annotation")
#                l_lipizones_loc = (
#                    data.get_lipizones()
#                    .index[
#                        (data.get_lipizones()["level"] == level)
#                        & (data.get_lipizones()["lipotype"] == lipotype)
#                    ]
#                    .tolist()
#                )[:1]
#                # return dash.no_update
#
#            # Record location and lipizones name
#            lipizones_index = l_lipizones_loc[0]
#            lipizones_string = "level " + level + " " + lipotype
#
#            change_made = False
#
#            # If lipizones has already been selected before, replace the index
#            if header_1 == lipizones_string:
#                lipizones_1_index = lipizones_index
#                change_made = True
#            elif header_2 == lipizones_string:
#                lipizones_2_index = lipizones_index
#                change_made = True
#            elif header_3 == lipizones_string:
#                lipizones_3_index = lipizones_index
#                change_made = True
#
#            # If it's a new lipizones selection, fill the first available header
#            if lipizones_string not in [header_1, header_2, header_2]:
#
#                # Check first slot available
#                if class_name_badge_1 == "d-none":
#                    header_1 = lipizones_string
#                    lipizones_1_index = lipizones_index
#                    class_name_badge_1 = "position-absolute"
#                elif class_name_badge_2 == "d-none":
#                    header_2 = lipizones_string
#                    lipizones_2_index = lipizones_index
#                    class_name_badge_2 = "position-absolute"
#                elif class_name_badge_3 == "d-none":
#                    header_3 = lipizones_string
#                    lipizones_3_index = lipizones_index
#                    class_name_badge_3 = "position-absolute"
#                else:
#                    logging.warning("More than 3 lipizones have been selected")
#                    return dash.no_update
#                change_made = True
#
#            if change_made:
#                logging.info(
#                    "Changes have been made to the lipizones selection or indexation,"
#                    + " propagating callback."
#                )
#                return (
#                    header_1,
#                    header_2,
#                    header_3,
#                    lipizones_1_index,
#                    lipizones_2_index,
#                    lipizones_3_index,
#                    class_name_badge_1,
#                    class_name_badge_2,
#                    class_name_badge_3,
#                    # None,
#                )
#            else:
#                return dash.no_update
#
#    return dash.no_update
#
#
#@app.callback(
#    Output("page-2-rgb-button", "disabled"),
#    Output("page-2-colormap-button", "disabled"),
#    Input("page-2-selected-lipizones-1", "data"),
#    Input("page-2-selected-lipizones-2", "data"),
#    Input("page-2-selected-lipizones-3", "data"),
#)
#def page_2_active_download(
#    lipizones_1_index, 
#    lipizones_2_index, 
#    lipizones_3_index
#):
#    """This callback is used to toggle on/off the display rgb and colormap buttons."""
#
#    # Get the current lipizones selection
#    l_lipizones_indexes = [
#        x for x in [lipizones_1_index, lipizones_2_index, lipizones_3_index] if x is not None and x != -1
#    ]
#    # If lipizones has been selected from the dropdown, activate button
#    if len(l_lipizones_indexes) > 0:
#        return False, False
#    else:
#        return True, True

#clientside_callback(
#    """
#    function(n_clicks){
#        if(n_clicks > 0){
#            domtoimage.toBlob(document.getElementById('page-2-graph-lipizones'))
#                .then(function (blob) {
#                    window.saveAs(blob, 'lipizones_plot.png');
#                }
#            );
#        }
#    }
#    """,
#    Output("page-2-download-image-button", "n_clicks"),
#    Input("page-2-download-image-button", "n_clicks"),
#)
#"""This clientside callback is used to download the current heatmap."""
