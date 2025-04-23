import os
import logging
import argparse
import logging.config
import logging.handlers
import urllib.parse as urlparse


import dash
import flask
import dash_core_components as dcc
from dash_extensions.enrich import Output, Input

# see https://community.plot.ly/t/nolayoutexception-on-deployment-of-multi-page-dash-app-example-
# code/12463/2?u=dcomfort
import regression.config_ssm as config
from regression.layouts.app import app
from regression.layouts.components import auth
from regression.layouts.layout import layout_nopage
from regression.layouts.components import labelling
from regression.layouts.components import metadata_parser
from regression.layouts.components import video_fetch
from regression.layouts.components import feature_kpis
from regression.layouts.components import regression_kpis
from regression.layouts.components.auth.layout import login_layout
from regression.utils.logging_init import initialize_logging_master
from regression.layouts.layout import nav_bar, labeler_navbar, login_navbar
from regression.layouts.components.feature_kpis.alert_debug.layout import alert_debug_page_layout
from regression.layouts.components import pipeline


logger = logging.getLogger(__name__)

DISABLE_AUTH = False


def parse_url(tab, href=None):
    """Parses the url and creates a states dictionary.
    Args:
        tab: page.
        href (str): url link.

    Returns: page.
    """
    states = {}
    if href:
        parse_result = urlparse.urlparse(href)
        query_dict = urlparse.parse_qs(parse_result.query)
        for key, value in query_dict.items():
            if value[0] == "True":
                value[0] = True
            elif value[0] == "False":
                value[0] = False
            states[key] = value[0]

    page = tab(states)
    return page


@app.callback(
    [
        Output("page-content", "children"),
        Output("nav-bar", "children")
    ],
    [
        Input("url", "pathname"),
        Input("url", "search")
    ],
)
def display_page(pathname, search):
    logger.debug(pathname)
    logger.debug(search)
    """Parses URLs and routes request to appropriate layout."""
    logger.info(pathname)
    # strip / at the end
    if pathname and pathname[-1] == "/":
        pathname = pathname[:-1]

    if not DISABLE_AUTH:
        # if the pathname starts with jwt the it has been redirected from the IDMS login console
        if pathname.startswith("/access"):
            logger.info(flask.request.args)
            token = search.split("=")[-1]
            # save the authentication information in database and set the cookie
            token_cookie, username = auth.util.save_auth_information_in_database(token)
            # set the cookie
            dash.callback_context.response.set_cookie(
                "auth_token", token_cookie, secure=True, httponly=True
            )
            # username cookie will be used while submitting the jobs
            dash.callback_context.response.set_cookie(
                "username", username, secure=True, httponly=True
            )
            return [dcc.Location(href="/", id="auth_home"), ""]
        # # authentication check. is session id cookie is not set then redirect to auth layout
        auth_token = flask.request.cookies.get("auth_token")
        username = flask.request.cookies.get("username")
        role = None
        logger.info(auth_token)
        # logger.info(config.cfg)
        if not auth_token or not username:
            return login_layout, login_navbar
        else:
            # verify auth token
            verfication_flag = auth.util.validate_auth_token(auth_token)
            if not verfication_flag:
                return [dcc.Location(href=config.cfg.get("IDMS")["auth_url"], id="auth"), ""]
            # auth token is valid, so fetch the role from the database
            role = auth.util.fetch_role_for_auth_token(auth_token)
            if not role:
                # is role is not present then authenticate the users again
                return [dcc.Location(href=config.cfg.get("IDMS")["auth_url"], id="auth"), ""]
        # serve pages based on url.

    if pathname == "":
        page = regression_kpis.analyze_kpis.layout.get_analyze_kpis_page()
    elif pathname == "/analyze-tag":
        page = parse_url(regression_kpis.analyze_kpis.layout.get_analyze_kpis_page, search)
    else:
        page = layout_nopage
    logger.debug(page)
    return page, nav_bar


def main():
    global DISABLE_AUTH, logger

    parser = argparse.ArgumentParser("")
    parser.add_argument("--sqs-queue-name", default="", type=str)
    parser.add_argument("--log-file-dir", default="", type=str)
    parser.add_argument("--config-file", default="", type=str)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--disable-auth", action="store_true")
    args = parser.parse_args()

    if args.log_file_dir:
        log_file_path = os.path.join(args.log_file_dir, "kpi_server.log")
    else:
        log_file_path = ""

    if args.disable_auth:
        DISABLE_AUTH = True
        auth.util.disable_auth()

    logger = logging.getLogger()
    initialize_logging_master(
        logger,
        "kpi-server",
        logging.INFO,
        rotating_log_path=log_file_path,
        syslog=False,
        console=args.debug,
    )

    if args.sqs_queue_name:
        config.cfg.ASG.sqs_queue_name = args.sqs_queue_name

    app.run_server(debug=args.debug, host="0.0.0.0", port=10004, threaded=True)


if __name__ == "__main__":
    main()
