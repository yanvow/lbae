###### IMPORT MODULES ######

# Official modules
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
import uuid
import dash_loading_spinners as dls
import logging
import dash_mantine_components as dmc

# Homemade modules
from lbae.app import app, data
from lbae.pages import (
    sidebar,
    home,
    load_slice,
    lipid_selection,
    lipid_selection_all_slices,
    region_analysis,
    threeD_exploration,
)
from lbae.config import basic_config
from lbae.modules.tools.memuse import logmem

###### DEFINE APP LAYOUT ######


# Responsive layout
def return_main_content():

    # list of empty lipid indexes for the dropdown of page 2bis
    empty_lipid_list = [-1 for i in range(data.get_slice_number())]

    # Record session id in case sessions need to be individualized (i.e. we handle better global variables)
    session_id = str(uuid.uuid4())

    # Define static content
    main_content = html.Div(
        children=[
            # To handle url since multi-page app
            dcc.Location(id="url", refresh=False),
            # Record session id, useful to trigger callbacks at initialization
            dcc.Store(id="session-id", data=session_id),
            # Record slice index, to keep track of current slice
            dcc.Store(id="dcc-store-slice-index", data=1),
            # Record the state of the range sliders for low and high resolution spectra in page 2
            dcc.Store(id="boundaries-low-resolution-mz-plot"),
            dcc.Store(id="boundaries-high-resolution-mz-plot"),
            # Record the lipids selected in page 2 (made with a dropdown for now)
            dcc.Store(id="page-2-selected-lipid-1", data=-1),
            dcc.Store(id="page-2-selected-lipid-2", data=-1),
            dcc.Store(id="page-2-selected-lipid-3", data=-1),
            dcc.Store(id="page-2-last-selected-lipids", data=[]),
            # Record the lipids selected in page 2bis
            dcc.Store(id="page-2bis-selected-lipid-1", data=empty_lipid_list),
            dcc.Store(id="page-2bis-selected-lipid-2", data=empty_lipid_list),
            dcc.Store(id="page-2bis-selected-lipid-3", data=empty_lipid_list),
            dcc.Store(id="page-2bis-last-selected-lipids", data=[]),
            # Record the shapes drawn in page 3
            dcc.Store(id="dcc-store-color-mask", data=[]),
            dcc.Store(id="dcc-store-reset", data=False),
            dcc.Store(id="dcc-store-shapes-and-masks", data=[]),
            dcc.Store(id="dcc-store-list-idx-lipids", data=[]),
            # Record the annotated paths drawn in page 3
            dcc.Store(id="page-3-dcc-store-path-heatmap"),
            # Record the computed spectra drawn in page 3
            dcc.Store(id="dcc-store-list-mz-spectra", data=[]),
            # Record the lipids expressed in the region in page 3
            dcc.Store(id="page-3-dcc-store-lipids-region", data=[]),
            # List of stores to compute loading bar
            dcc.Store(id="page-3-dcc-store-loading-1", data=False),
            dcc.Store(id="page-3-dcc-store-loading-2", data=False),
            dcc.Store(id="page-3-dcc-store-loading-3", data=False),
            dcc.Store(id="page-3-dcc-store-loading-4", data=False),
            dcc.Store(id="page-3-dcc-store-loading-5", data=False),
            # Actual app layout
            dbc.Container(
                fluid=True,
                children=[
                    sidebar.layout,
                    html.Div(id="content"),
                    dmc.Center(
                        dmc.Group(
                            [
                                dmc.Paper(
                                    dmc.Group(
                                        [
                                            dmc.Text("Slice: "),
                                            dmc.Slider(
                                                id="main-slider",
                                                min=1,
                                                max=data.get_slice_number(),
                                                marks=[
                                                    {"value": i, "label": str(i)}
                                                    for i in range(1, data.get_slice_number() + 1, 2)
                                                ],
                                                style={"width": "60vw"},
                                                className="pb-3",
                                                value=1,
                                            ),
                                        ],
                                        direction="row",
                                    ),
                                    padding="lg",
                                    shadow="md",
                                    radius="xl",
                                    withBorder=True,
                                ),
                                dmc.Button("Toggle documentation", id="button-doc"),
                                dmc.Space(w=30),
                            ],
                        ),
                        style={
                            "width": "100%",
                            "position": "fixed",
                            "bottom": 0,
                            "margin-left": "5%",
                            "margin-right": "5%",
                            "margin-bottom": "1%",
                            "left": "0",
                            "right": "0",
                        },
                    ),
                    # Space to ensure the slider for sections doesn't hide anything
                    dmc.Space(h=70),
                    # Documentation
                    dmc.Drawer(
                        id="drawer",
                        padding="md",
                        position="right",
                        size=500,
                        title="Page documentation",
                        children=[
                            dmc.Accordion(
                                children=[
                                    dmc.AccordionItem(
                                        children="""On any graph (heatmap or m/z plot), you can draw a square with your mouse to zoom in, 
        and double click to reset zoom level.""",
                                        label="Zoom",
                                    ),
                                    dmc.AccordionItem(
                                        children="""You can interact more with the figures (zoom, pan, reset axes, download) 
        using the modebard above them.""",
                                        label="Modebar",
                                    ),
                                    dmc.AccordionItem(
                                        children="""Most of the items in the app are embedded with advice.
            Just position your mouse over an item to get a tip on how to use it.""",
                                        label="Tooltips",
                                    ),
                                ],
                                iconPosition="right",
                                multiple=True,
                                id="acc",
                                # state={"1": True},
                            ),
                        ],
                    ),
                    dls.Tunnel(
                        id="main-spinner",
                        children=html.Div(id="empty-content"),
                        fullscreen=True,
                        fullscreen_style={"margin-left": "6rem", "padding-right": "7rem",},
                        debounce=200,
                        width=100,
                    ),
                ],
            ),
        ],
    )
    return main_content


main_content = return_main_content()

# Initialize app with main content
app.layout = main_content

# Give complete layout for callback validation
app.validation_layout = html.Div(
    [
        main_content,
        home.layout,
        load_slice.return_layout(basic_config=basic_config),
        lipid_selection.return_layout(basic_config=basic_config),
        lipid_selection_all_slices.return_layout(basic_config=basic_config),
        region_analysis.return_layout(basic_config=basic_config),
        threeD_exploration.return_layout(basic_config=basic_config),
    ]
)


###### APP CALLBACK FOR URL ######


@app.callback(Output("content", "children"), Output("empty-content", "children"), Input("url", "pathname"))
def render_page_content(pathname):
    logging.info("Page" + pathname + "has been selected" + logmem())

    # Set the content according to the current pathname
    if pathname == "/":
        page = home.layout

    elif pathname == "/load-slice":
        page = load_slice.return_layout(basic_config=basic_config)

    elif pathname == "/lipid-selection":
        page = lipid_selection.return_layout(basic_config=basic_config)

    elif pathname == "/lipid-selection-all-slices":
        page = lipid_selection_all_slices.return_layout(basic_config=basic_config)

    elif pathname == "/region-analysis":
        page = region_analysis.return_layout(basic_config=basic_config)

    elif pathname == "/3D-exploration":
        page = threeD_exploration.return_layout(basic_config=basic_config)

    else:
        # If the user tries to reach a different page, return a 404 message
        page = dbc.Jumbotron(
            children=[
                html.H1("404: Not found", className="text-danger"),
                html.Hr(),
                html.P(f"The pathname {pathname} was not recognised..."),
            ]
        )
    return page, ""


@app.callback(Output("drawer", "opened"), Input("button-doc", "n_clicks"), prevent_initial_call=True)
def drawer(n_clicks):
    return True


def run():
    app.run_server(port=8060, debug=True)


# Run app from local console (not gunicorn)
# if __name__ == "__main__":
#    app.run_server(port=8060, debug=False)

# pkill -P1 gunicorn
