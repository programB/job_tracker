import logging

from job_tracker_frontend.backend_comm import make_backend_call

logger = logging.getLogger(__name__)


def get_status():
    mandatory_params = {}
    optional_params = {}

    return make_backend_call(
        "health",
        mandatory_params,
        optional_params,
    )
