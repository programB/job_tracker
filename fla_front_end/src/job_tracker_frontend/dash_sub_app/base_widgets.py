from dash import dcc
from dash.html import Button

from .backend import allowed_choices

from .defaults import (
    default_bin,
    default_contract_type,
    default_end_date,
    default_job_level,
    default_job_mode,
    default_start_date,
    default_tag,
    earliest_date,
    latatest_date,
)

date_span_sel = dcc.DatePickerRange(
    id="date_span_sel",
    min_date_allowed=earliest_date.date().isoformat(),
    max_date_allowed=latatest_date.date().isoformat(),
    start_date=default_start_date.date().isoformat(),
    end_date=default_end_date.date().isoformat(),
    display_format="YYYY-MM-DD",
    clearable=False,
    first_day_of_week=1,
)

binning_dd = dcc.Dropdown(
    id="binning_dd",
    options=[{"label": bin, "value": bin} for bin in allowed_choices.bins],
    value=default_bin,
    clearable=False,
    className="dropdown",
)

tags_dd = dcc.Dropdown(
    id="tags_dd",
    options=[{"label": tag, "value": tag} for tag in allowed_choices.tags],
    value=default_tag,
    clearable=True,
    multi=True,
    className="dropdown",
)

contract_type_dd = dcc.Dropdown(
    id="contract_type_dd",
    options=[
        {"label": contract_type, "value": contract_type}
        for contract_type in allowed_choices.contract_types
    ],
    value=default_contract_type,
    clearable=True,
    className="dropdown",
)

job_mode_dd = dcc.Dropdown(
    id="job_mode_dd",
    options=[
        {"label": job_mode, "value": job_mode} for job_mode in allowed_choices.job_modes
    ],
    value=default_job_mode,
    clearable=True,
    className="dropdown",
)

job_level_dd = dcc.Dropdown(
    id="job_level_dd",
    options=[
        {"label": job_level, "value": job_level}
        for job_level in allowed_choices.job_levels
    ],
    value=default_job_level,
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
