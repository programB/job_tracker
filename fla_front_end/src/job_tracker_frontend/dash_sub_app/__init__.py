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
from dash import Dash, Input, Output, State
from dash.exceptions import PreventUpdate
from dash.html import Div
from flask import Flask, render_template

from .backend.exceptions import APIException, BackendNotAvailableException
from .backend.statistics import get_stats
from .components import chart1, stats_criteria_menu

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
        rendered_jinja_template = render_template("pages/dash_statistics.html")

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
        Input("submit_btn", "n_clicks"),
        State("date_span_sel", "start_date"),
        State("date_span_sel", "end_date"),
        State("binning_dd", "value"),
        State("tags_dd", "value"),
        State("contract_type_dd", "value"),
        State("job_mode_dd", "value"),
        State("job_level_dd", "value"),
    )
    def update_chart(
        n_clicks,
        start_date,
        end_date,
        binning,
        tags,
        contract_type,
        job_mode,
        job_level,
    ):

        date_format = "%Y-%m-%d"
        start_date = datetime.strptime(start_date, date_format)
        end_date = datetime.strptime(end_date, date_format)

        try:
            if n_clicks is None:
                raise AttributeError
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
            raise PreventUpdate
        except BackendNotAvailableException:
            # show pop-up -- connection issue
            raise PreventUpdate
        except APIException:
            # show pop-up -- unexpected API error
            # This should never happen
            raise PreventUpdate

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
            xaxis_title="publishing date",
            yaxis_title="offers count",
            # Legend is shown only when go.Figure contains more then 1 trace
            legend_title="Legend Title",
        )
        fig.update_xaxes(
            linecolor="black",  # X axis color
            ticks="outside",
            tickson="boundaries",
            # ticklen=20,
            # dtick="M1",
            # type='date',
            # tickmode set to 'linear' causes time to not be displayed
            tickmode="linear",
            # year (%Y) prepended with \n causes year to be shown below
            # day and month but only "once per year" (it will not be
            # repeated under each tick if it's unambiguous)
            tickformat="%d.%m\n%Y",
            # ticklabelmode="period",
        )
        fig.update_yaxes(
            linecolor="black",  # Y axis color
            gridcolor="#eeeeee",  # Horizontal grid (parallel to X axis !) color
        )
        # print(fig)  # to see resulting JSON structure describing the figure
        return fig

    return dash_app.server  # type: ignore
