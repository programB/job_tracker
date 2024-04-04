# The MIT License
#
# Copyright (c) 2024 programb
# Copyright (c) 2018 Todd Birchard
#
# Permission is hereby granted, free of charge,
# to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to
# deal in the Software without restriction, including
# without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom
# the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice
# shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
# ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import logging
from datetime import datetime

import plotly.graph_objects as go
from dash import Dash, Input, Output, State, no_update
from dash.html import Div, Li, Ul
from flask import Flask, render_template

from job_tracker_frontend.backend_comm.exceptions import (
    APIException,
    BackendNotAvailableException,
)
from job_tracker_frontend.backend_comm.statistics import get_stats

from .ui import chart1, stats_criteria_menu

logger = logging.getLogger(__name__)


class CustomDash(Dash):
    """Dash object with base html build from main Flask app templates

    See:
    Customizing Dash's HTML Index Template - Option 2 - interpolate_index
    at https://dash.plotly.com/external-resources
    and
    comments in the dash_statistics.html jinja2 template
    to learn how this works
    """

    def interpolate_index(self, **kwargs):  # type: ignore
        rendered_jinja_template = render_template("pages/statistics_dash.html")

        custom_index = rendered_jinja_template.format(
            metas=kwargs["metas"],
            favicon=kwargs["favicon"],
            css=kwargs["css"],
            app_entry=kwargs["app_entry"],
            config=kwargs["config"],
            scripts=kwargs["scripts"],
            renderer=kwargs["renderer"],
        )
        return custom_index


def init_dash_app(master_app: Flask) -> Flask:
    """Creates Dash app on top of existing Flask app

    Parameters
    ----------
    master_app : Flask

    Returns
    -------
    master_app : Flask

    Raises
    ------
    ValueError if Flask app not passed
    """

    if not isinstance(master_app, Flask):
        raise ValueError("master Flask app must be passed")

    dash_app = CustomDash(
        server=master_app,  # type: ignore
        routes_pathname_prefix="/dash_app/",
    )

    dash_app.layout = Div(
        children=[
            Div(
                children=[
                    Ul(
                        id="warnig_msg",
                        className="flashes",
                    )
                ],
            ),
            Div(
                children="This is a placeholder for a header with some general info",
                className="statistics-header",
            ),
            Div(
                children=[chart1],
                className="charts",
            ),
            Div(
                children=stats_criteria_menu,
                className="stats-criteria-menu",
            ),
        ],
        className="dash-main-div",
    )

    @dash_app.callback(
        Output("chart1", "figure"),
        Output("warnig_msg", "children"),
        Input("submit_btn", "n_clicks"),
        State("date_span_sel", "start_date"),
        State("date_span_sel", "end_date"),
        State("binning_dd", "value"),
        State("tags_dd", "value"),
        State("contract_type_dd", "value"),
        # TODO: job_mode is not yet collected when webpage offers are analysed
        #       see: Advertisement class in results_page module
        # State("job_mode_dd", "value"),
        State("job_level_dd", "value"),
    )
    def update_chart(
        n_clicks,
        start_date,
        end_date,
        binning,
        tags,
        contract_type,
        # TODO: job_mode is not yet collected when webpage offers are analysed
        #       see: Advertisement class in results_page module
        # job_mode,
        job_level,
    ):

        date_format = "%Y-%m-%d"
        start_date = datetime.strptime(start_date, date_format)
        end_date = datetime.strptime(end_date, date_format)

        try:
            if n_clicks is None:
                raise AttributeError

            # TODO: job_mode is not yet collected when webpage offers are analysed
            #       see: Advertisement class in results_page module
            job_mode = None
            stats = get_stats(
                start_date,
                end_date,
                binning,
                tags,
                contract_type,
                job_mode,
                job_level,
            )
        except AttributeError:
            # show pop-up -- invalid parameters
            # Ideally this should never happen
            return (
                no_update,
                Li(
                    children=[
                        (
                            "There was a problem when accessing backend service. "
                            "Failed to retrive statistics."
                        ),
                    ],
                    className="error",
                ),
            )
        except BackendNotAvailableException:
            # show pop-up -- connection issue
            return (
                no_update,
                Li(
                    children=[
                        (
                            "There was a problem when accessing backend service. "
                            "Failed to retrive statistics."
                        ),
                    ],
                    className="error",
                ),
            )

        except APIException:
            # show pop-up -- unexpected API error
            # This should never happen
            return (
                no_update,
                Li(
                    children=[
                        (
                            "There was a problem when accessing backend service. "
                            "Failed to retrive statistics."
                        ),
                    ],
                    className="error",
                ),
            )

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=stats.date,
                y=stats.counts,
                marker_color=["#f75403"] * len(stats),
                name="trace 1",  # name will appear in plot's legend
                # xperiod="M1",
                # xperiodalignment="middle",
            )
        )

        fig.update_layout(
            # Warning. Setting plot's background color to white will
            # cause axes and gird to become invisible because their default
            # color is white. Set their color in update_x(y)axes functions.
            plot_bgcolor="white",
            xaxis_title="offer publishing date",
            yaxis_title="count",
            # Legend is shown only when go.Figure contains more then 1 trace
            legend_title="Legend",
        )

        match binning:
            case "day":
                # year (%Y) prepended with \n causes year to be shown below
                # day and month but only "once per year" (it will not be
                # repeated under each tick if it's unambiguous)
                xaxis_tick_format = "%d.%m\n%Y"
                # If the axis `type` is "date", then you must convert the
                # time to milliseconds.
                # To set the interval between ticks to one day,
                # set `dtick` to 86400000.0
                # https://plotly.com/python/reference/layout/xaxis/#layout-xaxis-dtick
                xaxis_minor_d_tick = 86400000.0
                # Put a mark with description only every 7 days and only
                # minor tick for others
                # (this greatly improves speed when displaying many days).
                xaxis_d_tick = 7 * xaxis_minor_d_tick
            case "month":
                xaxis_tick_format = "%m\n%Y"
                xaxis_minor_d_tick = None
                xaxis_d_tick = "M1"
            case "year":
                xaxis_tick_format = "%Y"
                xaxis_minor_d_tick = None
                xaxis_d_tick = "M12"

        fig.update_xaxes(
            linecolor="black",  # X axis color
            ticks="outside",
            tickson="boundaries",
            type="date",
            dtick=xaxis_d_tick,
            # tickmode set to 'linear' causes time to not be displayed
            # tickmode="linear",
            tickformat=xaxis_tick_format,
            # ticklabelmode="period",
            minor_dtick=xaxis_minor_d_tick,
        )

        fig.update_yaxes(
            linecolor="black",  # Y axis color
            gridcolor="#eeeeee",  # Horizontal grid (parallel to X axis !) color
        )
        # print(fig)  # to see resulting JSON structure describing the figure
        # return fig for the first output and empty string for the warnig_msg output
        return fig, ""

    return dash_app.server  # type: ignore
