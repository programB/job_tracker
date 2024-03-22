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

from dash import Dash, dcc, html
from flask import Flask


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

    dash_app = Dash(
        server=master_app,
        routes_pathname_prefix="/dash_app/",
    )

    dash_app.layout = html.Div(
        children=[
            html.H1(
                children="A test subpage with 1 chart",
                style={"backgroundColor": "blue"},
            ),
            html.P(
                children=[
                    dcc.Graph(
                        figure={
                            # sample data
                            "data": [
                                {
                                    "x": (1, 2, 3),
                                    "y": (7, 14, 21),
                                    "type": "bar",
                                },
                            ],
                            "layout": {
                                "title": "A test title for bar chart no. 1",
                                "colorway": ["#f75403"],
                            },
                        },
                        className="chart",
                    ),
                    # another graph or dcc component(s) will
                    # go here
                ],
            ),
        ]
    )

    return dash_app.server
