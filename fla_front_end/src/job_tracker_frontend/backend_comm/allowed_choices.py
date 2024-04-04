import logging

from job_tracker_frontend.backend_comm import make_backend_call
from job_tracker_frontend.backend_comm.tags import get_tags

logger = logging.getLogger(__name__)

bins = ["day", "month", "year"]

try:
    tags = get_tags()
except Exception:  # pylint: disable=broad-exception-caught
    logger.error("Failed to get list of tags from the backend")
    tags = []

contract_types = ["Pełny etat", " Część etatu", " Dodatkowa / tymczasowa"]
# contract_types = ["full time", "part time", "temporary"]
job_modes = ["in office", "remote"]

# WARNING: These are just some key words that are used
#          in description of some job levels in the database
#          and this list is not comprehensive.
#          The way these is implemented in backend is subject to change.
job_levels = ["junior", "regular", "senior"]
