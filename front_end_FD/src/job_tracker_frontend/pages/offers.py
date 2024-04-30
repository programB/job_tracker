from flask import flash, render_template, request

from job_tracker_frontend.backend_comm.exceptions import (
    APIException,
    BackendNotAvailableException,
)
from job_tracker_frontend.backend_comm.offers import get_offers
from job_tracker_frontend.pages import bp


@bp.route("/offers")
def offers():
    # hard-coded for now
    # See backend api for other accepted values
    offers_per_subpage = 10
    try:
        subpage = request.args.get("subpage", default=1, type=int)
        ans = get_offers(offers_per_subpage, subpage)
    except (AttributeError, APIException, BackendNotAvailableException):
        flash(
            (
                "There was a problem when accessing backend service. "
                "Failed to retrive the list of offers."
            ),
            "error",
        )
        return render_template(
            "pages/offers.html",
            tot_subpages=0,
            curr_subpage=1,
            offs=[],
        )

    for off in ans["offers"]:
        # Return just the date (without time)
        off["collected"] = off["collected"].split("T")[0]
        off["posted"] = off["posted"].split("T")[0]
    return render_template(
        "pages/offers.html",
        tot_subpages=ans["info"]["tot_subpages"],
        curr_subpage=ans["info"]["curr_subpage"],
        offs=ans["offers"],
    )
