import logging
from datetime import datetime

import pandas as pd

from job_tracker_frontend.backend_comm import make_backend_call

from .validation import check_inputs

logger = logging.getLogger(__name__)


def get_stats(
    start_date: datetime,
    end_date: datetime,
    binning: str,
    tags,
    contract_type,
    job_mode,
    job_level,
):

    try:
        check_inputs(
            start_date, end_date, binning, tags, contract_type, job_mode, job_level
        )
    except AttributeError as e:
        logger.error("Invalid input data: %s", e)
        raise AttributeError from e

    mandatory_params = {
        "start_date": start_date.date().isoformat(),
        "end_date": end_date.date().isoformat(),
        "binning": binning,
    }
    optional_params = {}
    if tags:
        optional_params["tags"] = tags
    if contract_type:
        optional_params["contract_type"] = contract_type
    if job_mode:
        optional_params["job_mode"] = job_mode
    if job_level:
        optional_params["job_level"] = job_level

    return make_backend_call(
        "statistics",
        mandatory_params,
        optional_params,
        data_conditioning=transform_data,
    )


def transform_data(json_data):
    # Changing 'count' to 'counts' since former clashes with
    # panda's DataFrame internal method name. So data points like:
    # {"date": "2024-01-01", "count": 23},
    # will become:
    # {"date": "2024-01-01", "counts": 23},
    for point in json_data:
        point["counts"] = point.pop("count")
    # DataFrame is what plotly can easily use
    return pd.DataFrame.from_records(json_data)
