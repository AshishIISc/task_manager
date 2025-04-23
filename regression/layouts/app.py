import os
import dash_bootstrap_components as dbc
from dash_extensions.enrich import DashProxy, MultiplexerTransform
from flask_caching import Cache

external_stylesheets = [
    "/assets/custom.css",
    # Select from https://bootswatch.com/
    dbc.themes.FLATLY,
]

assets_path = os.path.join(os.getcwd(), "regression/layouts/assets")
app = DashProxy(
    __name__,
    assets_folder=assets_path,
    external_stylesheets=external_stylesheets,
    url_base_pathname="/",
    transforms=[MultiplexerTransform()],
)

cache = Cache(
    app.server,
    config={
        "CACHE_TYPE": "SimpleCache",
    },
)
app.config.suppress_callback_exceptions = True
server = app.server
