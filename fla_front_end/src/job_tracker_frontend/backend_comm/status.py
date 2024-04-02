import logging

import requests
from requests.exceptions import ConnectionError, Timeout

from .exceptions import APIException, BackendNotAvailableException

logger = logging.getLogger(__name__)


def get_status():

    mandatory_params = {}
    optional_params = {}
    try:
        response = requests.get(
            "http://job-tracker-backend:5000/api/health",
            params=mandatory_params | optional_params,
            timeout=2,
        )
    except Timeout as e:
        msg = "Backend service unavailable - connection timeout"
        logger.warning(msg + ": %s", e)
        raise BackendNotAvailableException(msg) from e
    except ConnectionError as e:
        msg = "Backend service unavailable - connection error"
        logger.warning(msg + ": %s", e)
        raise BackendNotAvailableException(msg) from e

    if response.status_code == 404:
        msg = "Backend service unavailable - 404"
        logger.warning(msg)
        raise BackendNotAvailableException(msg)

    if response.status_code == 200:
        # return transform_data(response.json())
        return response.json()

    msg = "Unknown API error."
    logger.error(
        msg + " Send request was: %s. Response was: %s",
        response.request.url,
        response.json(),
    )
    raise APIException(msg)
