from connexion.problem import problem
from flask import current_app, request
from sqlalchemy import exc

from job_tracker.models import JobOffer, joboffers_schema


def get_all():
    subpage = request.args.get("subpage", default=1, type=int)
    perpagelimit = request.args.get("perpagelimit", type=int)
    try:
        paginated_offers = JobOffer.query.order_by(JobOffer.posted).paginate(
            page=subpage, per_page=perpagelimit
        )
    except exc.OperationalError:
        current_app.logger.exception(
            ("Failed to connect to the database while trying query for offers")
        )
        return problem(
            status=500, title="database offline", detail="Check server health"
        )
    else:
        info = {
            "tot_subpages": paginated_offers.pages,
            "curr_subpage": paginated_offers.page,
        }
        offers = joboffers_schema.dump(paginated_offers)
        ans = {"info": info, "offers": offers}
        return ans  # Flask "jsonifies" ans object
