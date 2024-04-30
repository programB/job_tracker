import logging

from job_tracker_frontend.backend_comm import make_backend_call

logger = logging.getLogger(__name__)


def get_offers(
    perpagelimit: int,
    subpage: int,
):

    if perpagelimit not in range(10, 31):
        logger.error(
            "Invalid input perpagelimit must be in range [10,30] is %s", perpagelimit
        )
        raise AttributeError
    if perpagelimit % 10 != 0:
        logger.error(
            "Invalid input perpagelimit must multiple of 10 is %s", perpagelimit
        )
        raise AttributeError
    if subpage < 1:
        logger.error("Invalid input subpage must >=1 is %s", subpage)
        raise AttributeError

    mandatory_params = {
        "perpagelimit": perpagelimit,
        "subpage": subpage,
    }
    optional_params = {}
    return make_backend_call(
        "offers",
        mandatory_params,
        optional_params,
    )
