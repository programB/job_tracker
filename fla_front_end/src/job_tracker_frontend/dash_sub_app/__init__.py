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

from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, State, dcc
from dash.html import Button, Div
from flask import Flask, render_template


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

    chart1 = dcc.Graph(id="chart1", className="chart-tile")

    date_span_sel = dcc.DatePickerRange(
        id="date_span_sel",
        min_date_allowed=datetime(2024, 1, 1),
        max_date_allowed=datetime(2024, 12, 31),
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 31),
        display_format="YYYY-MM-DD",
        clearable=False,
        first_day_of_week=1,
    )

    bins = ["day", "month", "year"]
    binning_dd = dcc.Dropdown(
        id="binning_dd",
        options=[{"label": bin, "value": bin} for bin in bins],
        value="day",
        clearable=False,
        className="dropdown",
    )

    tags = []
    tags_dd = dcc.Dropdown(
        id="tags_dd",
        options=[{"label": tag, "value": tag} for tag in tags],
        value="",
        clearable=True,
        multi=True,
        className="dropdown",
    )

    contract_types = ["full time", "part time", "temporary"]
    contract_type_dd = dcc.Dropdown(
        id="contract_type_dd",
        options=[
            {"label": contract_type, "value": contract_type}
            for contract_type in contract_types
        ],
        value="",
        clearable=True,
        className="dropdown",
    )

    job_modes = ["in office", "remote"]
    job_mode_dd = dcc.Dropdown(
        id="job_mode_dd",
        options=[{"label": job_mode, "value": job_mode} for job_mode in job_modes],
        value="",
        clearable=True,
        className="dropdown",
    )

    job_levels = ["junior", "regular", "senior"]
    job_level_dd = dcc.Dropdown(
        id="job_level_dd",
        options=[{"label": job_level, "value": job_level} for job_level in job_levels],
        value="",
        clearable=True,
        className="dropdown",
    )

    submit_btn = Button(
        "Submit",
        id="submit_btn",
        n_clicks=0,
        style={
            "height": "40px",
            "width": "140px",
            "font": "inherit",
            "color": "#f75403",
            "backgroundColor": "white",
        },
    )

    # fmt: off
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
                children=[
                    Div(
                        children=[
                            Div(children=[Div(children=["Date span"], className="label"), Div(children=[date_span_sel], className="date-selector")]),
                            Div(children=[Div(children=["Binning"], className="label"), Div(children=[binning_dd], className="dropdown")]),
                        ],
                        className="h-sub-box",
                    ),
                    Div(
                        children=[
                            Div(children=[Div(children=["Contract type"], className="label"), Div(children=[contract_type_dd], className="dropdown")]),
                            Div(children=[Div(children=["Job mode"], className="label"), Div(children=[job_mode_dd], className="dropdown")]),
                            Div(children=[Div(children=["Job level"], className="label"), Div(children=[job_level_dd], className="dropdown")]),
                        ],
                        className="h-sub-box",
                    ),
                    Div(
                        children=[
                            Div(children=[Div(children=["Tags"], className="label"), Div(children=[tags_dd], className="long-dropdown")]),
                            Div(children=[Div(children=[submit_btn], className="button_sbm_box")]),
                        ],
                        className="h-sub-box",
                    ),
                ],
                className="stats-criteria-menu",
            ),
        ],
        className="dash-main-div",
    )
    # fmt: on

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
        y = (7, 14, 21)
        match job_level:
            case "junior":
                y = (7, 14, 21)
            case "regular":
                y = (11, 3, 1)
            case "senior":
                y = (7, 16, 5)
            case _:
                y = (0, 0, 0)

        dates = [
            datetime(2024, 1, 1),
            datetime(2024, 1, 2),
            datetime(2024, 1, 3),
        ]
        offer_data = pd.DataFrame(
            {
                "dates": dates,
                "counts": list(y),
            }
        )

        # plotyly express can be used as well
        # fig = px.bar(
        #     offer_data,
        #     x=offer_data.dates,
        #     y=offer_data.counts,
        #     color_discrete_sequence=["#f75403"] * len(dates),
        # )

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=offer_data.dates,
                y=offer_data.counts,
                marker_color=["#f75403"] * len(dates),
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
