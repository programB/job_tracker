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

    choices = ["choice 1", "choice 2", "choice 3", "choice 4"]

    dash_app.layout = html.Div(
        children=[
            html.Div(
                children="This is a placeholder for a header with some general info",
                className="statistics-header",
            ),
            html.Div(
                children=[
                    dcc.Graph(
                        id="chart1",
                        className="chart-tile",
                    ),
                    # another graph or dcc component(s) can go here
                ],
                className="charts",
            ),
            html.Div(
                children=[
                    dcc.Dropdown(
                        id="choice-dropdown",
                        options=[
                            {"label": choice, "value": choice} for choice in choices
                        ],
                        value="Mazowsze",
                        clearable=False,
                        className="dropdown",
                    ),
                ],
                className="stats-criteria-menu",
            ),
        ]
    )

    @dash_app.callback(
        Output("chart1", "figure"),
        Input("choice-dropdown", "value"),
    )
    def update_chart(choice):
        y = (7, 14, 21)
        match choice:
            case "choice 1":
                y = (7, 14, 21)
            case "choice 2":
                y = (11, 3, 1)
            case "choice 3":
                y = (7, 16, 5)
            case "choice 4":
                y = (0, 21, 8)

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
