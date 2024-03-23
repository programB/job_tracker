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

from dash import Dash, Input, Output, dcc, html
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

    def interpolate_index(self, **kwargs):
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
        server=master_app,
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

    dash_app.layout = html.Div(
        children=[
            html.Div(
                children="This is a placeholder for a header with some general info",
                className="statistics-header",
            ),
            html.Div(
                children=[chart1],
                className="charts",
            ),
            html.Div(
                children=[job_level_dd],
                className="stats-criteria-menu",
            ),
        ]
    )

    @dash_app.callback(
        Output("chart1", "figure"),
        Input("job_level_dd", "value"),
    )
    def update_chart(level):
        y = (7, 14, 21)
        match level:
            case "junior":
                y = (7, 14, 21)
            case "regular":
                y = (11, 3, 1)
            case "senior":
                y = (7, 16, 5)
            case _:
                y = (0, 0, 0)

        updated_figure = {
            # sample data
            "data": [
                {
                    "x": (1, 2, 3),
                    "y": y,
                    "type": "bar",
                },
            ],
            "layout": {
                "title": "A test title for bar chart no. 1",
                "colorway": ["#f75403"],
            },
        }
        return updated_figure

    return dash_app.server
