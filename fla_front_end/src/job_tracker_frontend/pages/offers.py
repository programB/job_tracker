from flask import render_template

from job_tracker_frontend.backend_comm.exceptions import (
    APIException,
    BackendNotAvailableException,
)
from job_tracker_frontend.backend_comm.offers import get_offers
from job_tracker_frontend.pages import bp


@bp.route("/offers")
def offers():
    try:
        offs = get_offers(10, 1)
    except (AttributeError, APIException, BackendNotAvailableException):
        print("Could not access backend service")
        return "<p> error while trying to communicate with backend service</p>"

    for off in offs:
        # Return just the date (without time)
        off["collected"] = off["collected"].split("T")[0]
        off["posted"] = off["posted"].split("T")[0]
    return render_template("pages/offers.html", offs=offs)
