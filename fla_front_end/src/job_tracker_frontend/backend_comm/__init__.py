import logging
import os

import requests
from requests.exceptions import ConnectionError, Timeout

from .exceptions import APIException, BackendNotAvailableException

logger = logging.getLogger(__name__)

# The value of BACKEND_URI is set by the load_dotenv function when application
# starts based on the contents of the .env file.
# If this this variable is set in the enviroment PRIOR to app execution
# load_dotenv will ignore the value in the .env file.
# The fallback value is used when none of the above places defines the variable.
backend_URI = os.getenv("BACKEND_URI", "http://localhost:5000/api/")


def make_backend_call(
    endpoint: str,
    mandatory_params: dict,
    optional_params: dict,
    data_conditioning=None,
    timeout: int = 2,
):
    try:
        response = requests.get(
            backend_URI + endpoint,
            params=mandatory_params | optional_params,
            timeout=timeout,
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
        if data_conditioning:
            return data_conditioning(response.json())
        return response.json()

    msg = "Unknown API error."
    logger.error(
        msg + " Send request was: %s. Response was: %s",
        response.request.url,
        response.json(),
    )
    raise APIException(msg)
