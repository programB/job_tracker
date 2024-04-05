from dash import dcc
from dash.html import Div

from .base_widgets import (
    binning_dd,
    contract_type_dd,
    date_span_sel,
    job_level_dd,
    job_mode_dd,
    submit_btn,
    tags_dd,
)

chart1 = dcc.Graph(id="chart1", className="chart-tile")
stats_criteria_menu = [
    Div(
        children=[
            Div(
                children=[
                    Div(children=["Date span"], className="label"),
                    Div(children=[date_span_sel], className="date-selector"),
                ]
            ),
            Div(
                children=[
                    Div(children=["Binning"], className="label"),
                    Div(children=[binning_dd], className="dropdown"),
                ]
            ),
        ],
        className="h-sub-box",
    ),
    Div(
        children=[
            Div(
                children=[
                    Div(children=["Contract type"], className="label"),
                    Div(children=[contract_type_dd], className="dropdown"),
                ]
            ),
            # TODO: job_mode is not yet collected when webpage offers are analysed
            #       see: Advertisement class in results_page module
            # Div(
            #     children=[
            #         Div(children=["Job mode"], className="label"),
            #         Div(children=[job_mode_dd], className="dropdown"),
            #     ]
            # ),
            Div(
                children=[
                    Div(children=["Job level"], className="label"),
                    Div(children=[job_level_dd], className="dropdown"),
                ]
            ),
        ],
        className="h-sub-box",
    ),
    Div(
        children=[
            Div(
                children=[
                    Div(children=["Tags"], className="label"),
                    Div(children=[tags_dd], className="long-dropdown"),
                ]
            ),
            Div(children=[Div(children=[submit_btn], className="button_sbm_box")]),
        ],
        className="h-sub-box",
    ),
]
