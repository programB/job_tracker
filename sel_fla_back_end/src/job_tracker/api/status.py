import json
import logging
import os
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from sqlalchemy import text

from job_tracker.database import db

logger = logging.getLogger(__name__)


def get_selenium_grid_status():
    """Check if selenium grid service is up and accepting jobs"""
    # This is the command used in the official docker images of selenium
    # curl -sSL http://${HOST}:${PORT}/wd/hub/status | jq -r '.value.ready' \
    #                                           | grep -q "true" || exit 1
    selenium_grid_url = os.getenv("SELENIUM_GRID_URL")
    selenium_grid_port = os.getenv("SELENIUM_GRID_PORT", "4444")
    status_url = rf"{selenium_grid_url}:{selenium_grid_port}/wd/hub/status"
    if not status_url.startswith(r"http://"):
        logger.critical(
            (
                "Checking for selenium grid status: url does not look to be valid: %s. "
                "Check skipped for security reasons.",
                status_url,
            )
        )
        return False
    try:
        # Silence bandit security check
        # there is little chance status_url can get abused
        with urlopen(status_url) as response:  # nosec B310
            msg = response.read()
    except (URLError, HTTPError) as e:
        is_OK = False
        logger.warning(
            (
                "Checking for selenium grid status resulted in error: %s. "
                "Service considered NOT ready"
            ),
            str(e),
        )
    else:
        is_OK = json.loads(msg).get("value").get("ready")
        result = "" if is_OK else "NOT"
        logger.info(
            "Checking for selenium grid status: service is %s ready",
            result,
        )
    return is_OK


def get_database_status(sqldb):
    try:
        sqldb.session.execute(text("SELECT 1"))
    except Exception as e:
        is_OK = False
        logger.warning(
            "Checking for database status resulted in error: %s",
            str(e),
        )
    else:
        is_OK = True
        logger.info("Checking for database status: database is accepting queries")

    return is_OK


def health():
    # This is and endpoint so the application context is active
    # here and thus we can use it to call the db
    database_status = get_database_status(sqldb=db)
    return {
        "is_selenium_grid_healthy": get_selenium_grid_status(),
        "is_database_online": database_status,
    }
