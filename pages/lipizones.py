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

    #page = (
    #    html.Div([
    #dmc.MultiSelect(
    #    id="page-2-dropdown-lipizones",
    #    data=[{'value': f'lipid-{i}', 'label': f'Lipid {i}'} for i in range(1, 11)],
    #    searchable=True,
    #    nothingFound="No lipid found",
    #    radius="md",
    #    size="xs",
    #    placeholder="Choose up to 3 lipizones",
    #    clearable=False,
    #    maxSelectedValues=3,
    #    transitionDuration=150,
    #    transition="pop-top-left",
    #    transitionTimingFunction="ease",
    #    style={
    #        "width": "20em",
    #    },
    #),
    #dmc.Badge(
    #    id="page-2-badge-lipizones-1",
    #    color="red",
    #    variant="filled",
    #    class_name="d-none",
    #    style={"right": "1%", "top": "4em"},
    #),
    #dmc.Badge(
    #    id="page-2-badge-lipizones-2",
    #    color="teal",
    #    variant="filled",
    #    class_name="d-none",
    #    style={"right": "1%", "top": "6em"},
    #),
    #dmc.Badge(
    #    id="page-2-badge-lipizones-3",
    #    color="blue",
    #    variant="filled",
    #    class_name="d-none",
    #    style={"right": "1%", "top": "8em"},
    #),
    #])
    #)

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
                        #dbc.Spinner(
                        #    color="info",
                        #    spinner_style={
                        #        "margin-top": "40%",
                        #        "width": "3rem",
                        #        "height": "3rem",
                        #    },
                        #    children=dcc.Graph(
                        #        id="page-2-graph-heatmap-mz-selection",
                        #        config=basic_config
                        #        | {
                        #            "toImageButtonOptions": {
                        #                "format": "png",
                        #                "filename": "brain_lipid_selection",
                        #                "scale": 2,
                        #            }
                        #        }
                        #        | {"staticPlot": False},
                        #        style={
                        #            "width": "95%",
                        #            "height": "95%",
                        #            "position": "absolute",
                        #            "left": "0",
                        #            "top": "0",
                        #            "background-color": "#1d1c1f",
                        #        },
                        #        figure=figures.compute_heatmap_per_mz(
                        #            slice_index,
                        #            800,
                        #            802,
                        #            cache_flask=cache_flask,
                        #        ),
                        #    ),
                        #),
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
                                            id="page-2-dropdown-lipids",
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
                            id="page-2-badge-lipid-1",
                            children="name-lipid-1",
                            color="red",
                            variant="filled",
                            class_name="d-none",
                            style={"right": "1%", "top": "4em"},
                        ),
                        dmc.Badge(
                            id="page-2-badge-lipid-2",
                            children="name-lipid-2",
                            color="teal",
                            variant="filled",
                            class_name="d-none",
                            style={"right": "1%", "top": "6em"},
                        ),
                        dmc.Badge(
                            id="page-2-badge-lipid-3",
                            children="name-lipid-3",
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

@app.callback(
    Output("page-2-badge-lipizones-1", "children"),
    Output("page-2-badge-lipizones-2", "children"),
    Output("page-2-badge-lipizones-3", "children"),
    Output("page-2-badge-lipizones-1", "class_name"),
    Output("page-2-badge-lipizones-2", "class_name"),
    Output("page-2-badge-lipizones-3", "class_name"),
    Input("page-2-dropdown-lipizones", "value")
)
def update_badges(selected_lipids):
    if selected_lipids is None:
        selected_lipids = []

    badge_classes = ["d-none", "d-none", "d-none"]
    badge_texts = ["", "", ""]

    for i, lipid in enumerate(selected_lipids):
        badge_classes[i] = "position-absolute"
        badge_texts[i] = lipid

    return badge_texts[0], badge_texts[1], badge_texts[2], badge_classes[0], badge_classes[1], badge_classes[2]


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
#    l_lipid_names,
#    class_name_badge_1,
#    class_name_badge_2,
#    class_name_badge_3,
#    slice_index,
#    lipid_1_index,
#    lipid_2_index,
#    lipid_3_index,
#    header_1,
#    header_2,
#    header_3,
#):
#    """This callback adds the selected lipid to the selection."""
#
#    logging.info("Entering function to update lipid data")
#
#    # Find out which input triggered the function
#    id_input = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
#    value_input = dash.callback_context.triggered[0]["prop_id"].split(".")[1]
#
#    # if page-2-dropdown-lipizones is called while there's no lipid name defined, it means the page
#    # just got loaded
#    if len(id_input) == 0 or (id_input == "page-2-dropdown-lipizones" and l_lipid_names is None):
#        return "", "", "", -1, -1, -1, "d-none", "d-none", "d-none"  # , None
#
#    # If one or several lipids have been deleted
#    if l_lipid_names is not None:
#        if len(l_lipid_names) < len(
#            [x for x in [lipid_1_index, lipid_2_index, lipid_3_index] if x != -1]
#        ):
#            logging.info("One or several lipids have been deleter. Cleaning lipid badges now.")
#            for idx_header, header in enumerate([header_1, header_2, header_3]):
#                found = False
#                for lipid_name in l_lipid_names:
#                    if lipid_name == header:
#                        found = True
#                if not found:
#                    if idx_header == 0:
#                        header_1 = ""
#                        lipid_1_index = -1
#                        class_name_badge_1 = "d-none"
#                    if idx_header == 1:
#                        header_2 = ""
#                        lipid_2_index = -1
#                        class_name_badge_2 = "d-none"
#                    if idx_header == 2:
#                        header_3 = ""
#                        lipid_3_index = -1
#                        class_name_badge_3 = "d-none"
#
#            return (
#                header_1,
#                header_2,
#                header_3,
#                lipid_1_index,
#                lipid_2_index,
#                lipid_3_index,
#                class_name_badge_1,
#                class_name_badge_2,
#                class_name_badge_3,
#            )
#
#    # Otherwise, update selection or add lipid
#    if (
#        id_input == "page-2-dropdown-lipizones" and l_lipid_names is not None
#    ) or id_input == "main-slider":
#
#        # If a new slice has been selected
#        if id_input == "main-slider":
#
#            # for each lipid, get lipid name, structure and cation
#            for header in [header_1, header_2, header_3]:
#
#                if len(header) > 2:
#                    name, structure, cation = header.split(" ")
#
#                    # Find lipid location
#                    l_lipid_loc_temp = (
#                        data.get_annotations()
#                        .index[
#                            (data.get_annotations()["name"] == name)
#                            & (data.get_annotations()["structure"] == structure)
#                            & (data.get_annotations()["cation"] == cation)
#                        ]
#                        .tolist()
#                    )
#                    l_lipid_loc = [
#                        l_lipid_loc_temp[i]
#                        for i, x in enumerate(
#                            data.get_annotations().iloc[l_lipid_loc_temp]["slice"] == slice_index
#                        )
#                        if x
#                    ]
#
#                    # Fill list with first annotation that exists if it can't find one for the
#                    # current slice
#                    if len(l_lipid_loc) == 0:
#                        l_lipid_loc = l_lipid_loc_temp[:1]
#
#                    # Record location and lipid name
#                    lipid_index = l_lipid_loc[0]
#
#                    # If lipid has already been selected before, replace the index
#                    if header_1 == header:
#                        lipid_1_index = lipid_index
#                    elif header_2 == header:
#                        lipid_2_index = lipid_index
#                    elif header_3 == header:
#                        lipid_3_index = lipid_index
#
#            logging.info("Returning updated lipid data")
#            return (
#                header_1,
#                header_2,
#                header_3,
#                lipid_1_index,
#                lipid_2_index,
#                lipid_3_index,
#                class_name_badge_1,
#                class_name_badge_2,
#                class_name_badge_3,
#            )
#
#        # If lipids have been added from dropdown menu
#        elif id_input == "page-2-dropdown-lipizones":
#            # Get the lipid name and structure
#            name, structure, cation = l_lipid_names[-1].split(" ")
#
#            # Find lipid location
#            l_lipid_loc = (
#                data.get_annotations()
#                .index[
#                    (data.get_annotations()["name"] == name)
#                    & (data.get_annotations()["structure"] == structure)
#                    & (data.get_annotations()["slice"] == slice_index)
#                    & (data.get_annotations()["cation"] == cation)
#                ]
#                .tolist()
#            )
#
#            # If several lipids correspond to the selection, we have a problem...
#            if len(l_lipid_loc) > 1:
#                logging.warning("More than one lipid corresponds to the selection")
#                l_lipid_loc = [l_lipid_loc[-1]]
#
#            if len(l_lipid_loc) < 1:
#                logging.warning("No lipid annotation exist. Taking another slice annotation")
#                l_lipid_loc = (
#                    data.get_annotations()
#                    .index[
#                        (data.get_annotations()["name"] == name)
#                        & (data.get_annotations()["structure"] == structure)
#                        & (data.get_annotations()["cation"] == cation)
#                    ]
#                    .tolist()
#                )[:1]
#                # return dash.no_update
#
#            # Record location and lipid name
#            lipid_index = l_lipid_loc[0]
#            lipid_string = name + " " + structure + " " + cation
#
#            change_made = False
#
#            # If lipid has already been selected before, replace the index
#            if header_1 == lipid_string:
#                lipid_1_index = lipid_index
#                change_made = True
#            elif header_2 == lipid_string:
#                lipid_2_index = lipid_index
#                change_made = True
#            elif header_3 == lipid_string:
#                lipid_3_index = lipid_index
#                change_made = True
#
#            # If it's a new lipid selection, fill the first available header
#            if lipid_string not in [header_1, header_2, header_2]:
#
#                # Check first slot available
#                if class_name_badge_1 == "d-none":
#                    header_1 = lipid_string
#                    lipid_1_index = lipid_index
#                    class_name_badge_1 = "position-absolute"
#                elif class_name_badge_2 == "d-none":
#                    header_2 = lipid_string
#                    lipid_2_index = lipid_index
#                    class_name_badge_2 = "position-absolute"
#                elif class_name_badge_3 == "d-none":
#                    header_3 = lipid_string
#                    lipid_3_index = lipid_index
#                    class_name_badge_3 = "position-absolute"
#                else:
#                    logging.warning("More than 3 lipids have been selected")
#                    return dash.no_update
#                change_made = True
#
#            if change_made:
#                logging.info(
#                    "Changes have been made to the lipid selection or indexation,"
#                    + " propagating callback."
#                )
#                return (
#                    header_1,
#                    header_2,
#                    header_3,
#                    lipid_1_index,
#                    lipid_2_index,
#                    lipid_3_index,
#                    class_name_badge_1,
#                    class_name_badge_2,
#                    class_name_badge_3,
#                    # None,
#                )
#            else:
#                return dash.no_update
#
#    return dash.no_update
