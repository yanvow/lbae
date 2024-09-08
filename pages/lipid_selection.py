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
                                figure=figures.compute_grey_image_per_slice(
                                    slice_index
                                ),
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
    Input("main-slider", "data"),
    Input("page-2-badge-lipid-1", "children"),
    Input("page-2-badge-lipid-2", "children"),
    Input("page-2-badge-lipid-3", "children"),
    Input("page-2-rgb-button", "n_clicks"),
    Input("page-2-colormap-button", "n_clicks"),
    State("page-2-badge-input", "children"),
)
def page_2_plot_graph_heatmap_selection(
    slice_index,
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
        or (
            (id_input == "main-slider")
            and (
                graph_input == "Current input: " + "Lipid selection colormap"
                or graph_input == "Current input: " + "Lipid selection RGB"
                or graph_input == "Current input: " + "None"
            )
        )
    ):
        logging.info("Lipid selection has been done, propagating callback.")
        
        l_lipid_names = [header_1, header_2, header_3]

        if (
            id_input == "page-2-badge-lipid-1"
            or id_input == "page-2-badge-lipid-2"
            or id_input == "page-2-badge-lipid-3"
        ):
            
            if (
                graph_input == "Current input: " + "Lipid selection colormap"
            ):
                return (
                    figures.compute_heatmap_per_lipid_selection(
                        slice_index,
                        l_lipid_names=l_lipid_names
                    ),
                    "Current input: " + "Lipid selection colormap",
                )
            
            elif(
                graph_input == "Current input: " + "Lipid selection RGB"
            ):
                return (
                    figures.compute_rgb_image_per_lipid_selection(
                        slice_index,
                        l_lipid_names=l_lipid_names
                    ),
                    "Current input: " + "Lipid selection RGB",
            )

        # Check if the current plot must be a heatmap
        elif (
            id_input == "page-2-colormap-button"
            or (
                id_input == "main-slider"
                and graph_input == "Current input: " + "Lipid selection colormap"
            )
        ):
            return (
                figures.compute_heatmap_per_lipid_selection(
                    slice_index,
                    l_lipid_names=l_lipid_names
                ),
                "Current input: " + "Lipid selection colormap",
            )

        # Or if the current plot must be an RGB image
        elif (
            id_input == "page-2-rgb-button"
            or (
                id_input == "main-slider"
                and graph_input == "Current input: " + "Lipid selection RGB"
            )
        ):
            return (
                figures.compute_rgb_image_per_lipid_selection(
                    slice_index,
                    l_lipid_names=l_lipid_names
                ),
                "Current input: " + "Lipid selection RGB",
            )

        # Plot grey image by default
        else:
            logging.info("Right before calling the graphing function")
            return (
                figures.compute_grey_image_per_slice(
                    slice_index
                ),
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
    value_input = dash.callback_context.triggered[0]["prop_id"].split(".")[1]

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
    Output("page-2-download-data", "data"),
    Input("page-2-download-data-button", "n_clicks"),
    State("page-2-selected-lipid-1", "data"),
    State("page-2-selected-lipid-2", "data"),
    State("page-2-selected-lipid-3", "data"),
    State("main-slider", "data"),
    State("page-2-badge-input", "children"),
    prevent_initial_call=True,
)
def page_2_download(
    n_clicks,
    lipid_1_index,
    lipid_2_index,
    lipid_3_index,
    slice_index,
    graph_input,
):
    """This callback is used to generate and download the data in proper format."""

    # Current input is lipid selection
    if (
        graph_input == "Current input: " + "Lipid selection colormap"
        or graph_input == "Current input: " + "Lipid selection RGB"
    ):

        l_lipids_indexes = [
            x for x in [lipid_1_index, lipid_2_index, lipid_3_index] if x is not None and x != -1
        ]
        # If lipids has been selected from the dropdown, filter them in the df and download them
        if len(l_lipids_indexes) > 0:

            def to_excel(bytes_io):
                xlsx_writer = pd.ExcelWriter(bytes_io, engine="xlsxwriter")
                data.get_annotations().iloc[l_lipids_indexes].to_excel(
                    xlsx_writer, index=False, sheet_name="Selected lipids"
                )
                for i, index in enumerate(l_lipids_indexes):
                    name = (
                        data.get_annotations().iloc[index]["name"]
                        + "_"
                        + data.get_annotations().iloc[index]["structure"]
                        + "_"
                        + data.get_annotations().iloc[index]["cation"]
                    )

                    # Need to clean name to use it as a sheet name
                    name = name.replace(":", "").replace("/", "")
                    lb = float(data.get_annotations().iloc[index]["min"]) - 10**-2
                    hb = float(data.get_annotations().iloc[index]["max"]) + 10**-2
                    x, y = figures.compute_spectrum_high_res(
                        slice_index,
                        lb,
                        hb,
                        plot=False,
                        standardization=apply_transform,
                        cache_flask=cache_flask,
                    )
                    df = pd.DataFrame.from_dict({"m/z": x, "Intensity": y})
                    df.to_excel(xlsx_writer, index=False, sheet_name=name[:31])
                xlsx_writer.save()

            return dcc.send_data_frame(to_excel, "my_lipid_selection.xlsx")

    # Current input is manual boundaries selection from input box
    if graph_input == "Current input: " + "m/z boundaries":
        lb, hb = float(lb), float(hb)
        if lb >= 400 and hb <= 1600 and hb - lb > 0 and hb - lb < 10:

            def to_excel(bytes_io):

                # Get spectral data
                mz, intensity = figures.compute_spectrum_high_res(
                    slice_index,
                    lb - 10**-2,
                    hb + 10**-2,
                    force_xlim=True,
                    standardization=apply_transform,
                    cache_flask=cache_flask,
                    plot=False,
                )

                # Turn to dataframe
                dataset = pd.DataFrame.from_dict({"m/z": mz, "Intensity": intensity})

                # Export to excel
                xlsx_writer = pd.ExcelWriter(bytes_io, engine="xlsxwriter")
                dataset.to_excel(xlsx_writer, index=False, sheet_name="mz selection")
                xlsx_writer.save()

            return dcc.send_data_frame(to_excel, "my_boundaries_selection.xlsx")

    # Current input is boundaries from the low-res m/z plot
    elif graph_input == "Current input: " + "Selection from high-res m/z graph":
        if bound_high_res is not None:
            # Case the zoom is high enough
            if bound_high_res[1] - bound_high_res[0] <= 3:

                def to_excel(bytes_io):

                    # Get spectral data
                    bound_high_res = json.loads(bound_high_res)
                    mz, intensity = figures.compute_spectrum_high_res(
                        slice_index,
                        bound_high_res[0],
                        bound_high_res[1],
                        standardization=apply_transform,
                        cache_flask=cache_flask,
                        plot=False,
                    )

                    # Turn to dataframe
                    dataset = pd.DataFrame.from_dict({"m/z": mz, "Intensity": intensity})

                    # Export to excel
                    xlsx_writer = pd.ExcelWriter(bytes_io, engine="xlsxwriter")
                    dataset.to_excel(xlsx_writer, index=False, sheet_name="mz selection")
                    xlsx_writer.save()

                return dcc.send_data_frame(to_excel, "my_boundaries_selection.xlsx")

    return dash.no_update


clientside_callback(
    """
    function(n_clicks){
        if(n_clicks > 0){
            domtoimage.toBlob(document.getElementById('page-2-graph-heatmap-mz-selection'))
                .then(function (blob) {
                    window.saveAs(blob, 'lipid_selection_plot.png');
                }
            );
        }
    }
    """,
    Output("page-2-download-image-button", "n_clicks"),
    Input("page-2-download-image-button", "n_clicks"),
)
"""This clientside callback is used to download the current heatmap."""


@app.callback(
    Output("page-2-rgb-button", "disabled"),
    Output("page-2-colormap-button", "disabled"),
    Input("page-2-badge-lipid-1", "children"),
    Input("page-2-badge-lipid-2", "children"),
    Input("page-2-badge-lipid-3", "children"),
)
def page_2_active_download(lipid_1_index, lipid_2_index, lipid_3_index):
    """This callback is used to toggle on/off the display rgb and colormap buttons."""

    logging.info("Entering function to toggle on/off the display rgb and colormap buttons")

    logging.info("Lipid indexes are: " + str(lipid_1_index) + " " + str(lipid_2_index) + " " + str(lipid_3_index))

    # Get the current lipid selection
    l_lipids_indexes = [
        x for x in [lipid_1_index, lipid_2_index, lipid_3_index] if x is not None and x != -1
    ]
    # If lipids has been selected from the dropdown, activate button
    if len(l_lipids_indexes) > 0:
        return False, False
    else:
        return True, True
