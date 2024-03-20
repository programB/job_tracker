import logging

from connexion.problem import problem
from flask import request
from sqlalchemy import exc

from job_tracker.models import JobOffer, joboffers_schema

logger = logging.getLogger(__name__)


def get_all():
    subpage = request.args.get("subpage", default=1, type=int)
    perpagelimit = request.args.get("perpagelimit", type=int)
    try:
        paginated_offers = JobOffer.query.paginate(page=subpage, per_page=perpagelimit)
    except exc.OperationalError:
        logger.exception(
            ("Failed to connect to the database while trying query for offers")
        )
        return problem(
            status=500, title="database offline", detail="Check server health"
        )
    else:
        return joboffers_schema.dump(paginated_offers)
