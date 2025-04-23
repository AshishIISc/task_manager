from dash import dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from regression.layouts.app import app

table_styling_params = {
    "sort_action": "native",
    "filter_action": "native",
    "merge_duplicate_headers": True,
    "style_table": {"overflowX": "scroll"},
    "style_cell": {"textAlign": "center"},
    "style_data": {"whiteSpace": "normal", "height": "auto"},
    "style_data_conditional": [
        {"if": {"row_index": "odd"}, "backgroundColor": "rgb(248, 248, 248)"}
    ],
    "style_header": {
        "backgroundColor": "rgb(230, 230, 230)",
        "fontWeight": "bold",
    },
}

# see https://dash.plot.ly/external-resources to alter header, footer and favicon
app.index_string = """
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>Netradyne KPI Tool</title>
            {%favicon%}
            {%css%}
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    """

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Div(id="nav-bar"),
        html.Div(id="page-content"),
    ]
)


# Common layouts
nav_bar = dbc.NavbarSimple(
    [
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem("Analyze Tag", href="/analyze-tag"),
                dbc.DropdownMenuItem("Compare Tags", href="/compare-tags"),
                dbc.DropdownMenuItem("Recent Jobs", href="/recent-jobs"),
                dbc.DropdownMenuItem("Submit Job", href="/submit-jobs"),
                dbc.DropdownMenuItem("Update Dataset", href="/update-dataset"),
                dbc.DropdownMenuItem("Video Player", href="/video"),
            ],
            nav=True,
            in_navbar=True,
            label="Regression-KPIs",
        ),
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem("Labelers Stat", header=True),
                dbc.DropdownMenuItem("KPI Audit Monitor", href="/kpi-audit-monitor"),
                dbc.DropdownMenuItem("Labeler's Throughput", href="/labeler-stats"),
                dbc.DropdownMenuItem("Labeler's Disagreements", href="/labeler-disagreements"),
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem("Label Video", header=True),
                dbc.DropdownMenuItem("AAID Review", href="/aaid-review"),
                dbc.DropdownMenuItem("AAID Attribute Labelling", href="/aaid-attribute-labelling"),
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem("Configuration", header=True),
                dbc.DropdownMenuItem(
                    "Modify Global Review Tags", href="/modify-global-review-tags"
                ),
                dbc.DropdownMenuItem(
                    "Modify Feature Review Tags", href="/modify-feature-review-tags"
                ),
                dbc.DropdownMenuItem(
                    "Modify Attribute Labelling Config",
                    href="/modify-attribute-labelling-config",
                ),
                dbc.DropdownMenuItem(divider=True),
                dbc.DropdownMenuItem("CSV Upload", header=True),
                dbc.DropdownMenuItem(
                    "Submit Alert Review Tags CSV", href="/submit-alert-review-tags"
                ),
                dbc.DropdownMenuItem(
                    "Submit Alert Attribute CSV", href="/submit-alert-attribute-csv"
                ),
                dbc.DropdownMenuItem("Create New Alerts from CSV", href="/create-new-alerts"),
            ],
            nav=True,
            in_navbar=True,
            label="Labelling",
        ),
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem("Field-KPI Reports", href="/field-kpi-reports"),
                dbc.DropdownMenuItem("Label Requests", href="/label-requests"),
                dbc.DropdownMenuItem("Label Request KPIs", href="/label-request-kpis"),
                dbc.DropdownMenuItem("Alert Debug", href="/alert-debug"),
            ],
            nav=True,
            in_navbar=True,
            label="Feature-KPIs",
        ),
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem("Alert File Parser", href="/alert-file-parser"),
                dbc.DropdownMenuItem("Observation Zip Parser", href="/observation-zip-parser"),
                dbc.DropdownMenuItem("Recent Jobs", href="/parser-recent-jobs"),
            ],
            nav=True,
            in_navbar=True,
            label="Metadata Parser",
        ),
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem("Past Alert/Obs Video Fetch", href="/video-fetch-past-job"),
                dbc.DropdownMenuItem("Stream Video Fetch", href="/video-fetch-submit-job"),
                dbc.DropdownMenuItem("Recent Jobs", href="/video-fetch-recent-job"),
            ],
            nav=True,
            in_navbar=True,
            label="Video Fetch",
        ),
        dbc.NavItem(dbc.NavLink("Pipelines", href="/automated-pipeline")),
        html.Form(
            [html.Button("Logout", type="submit", id="logout", className="btn btn-info")],
            action="/logout",
            method="post",
            className="logout_form",
        ),  # code for /logout is inside auth.layouts page
    ],
    brand="Netradyne",
    sticky="top",
    color="primary",
    dark=True,
    fluid=True,
)


layout_nopage = html.Div([html.P(["404 Page not found"])], className="no-page")


labeler_navbar = dbc.NavbarSimple(
    [
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem("Video Player", href="/video"),
                dbc.DropdownMenuItem("AAID Review", href="/aaid-review"),
                dbc.DropdownMenuItem("AAID Attribute Labelling", href="/aaid-attribute-labelling"),
                dbc.DropdownMenuItem("Alert Debug", href="/alert-debug"),
            ],
            nav=True,
            in_navbar=True,
            label="Menu",
        ),
        html.Form(
            [html.Button("Logout", type="submit", id="logout", className="btn btn-info")],
            action="/logout",
            method="post",
            className="logout_form",
        ),
    ],
    brand="Netradyne",
    sticky="top",
    color="primary",
    dark=True,
    fluid=True,
)


login_navbar = dbc.NavbarSimple(
    brand="Netradyne",
    sticky="top",
    color="primary",
    dark=True,
    fluid=True,
)
