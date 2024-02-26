from flask import request

from job_tracker.models import JobOffer, joboffers_schema


def get_all():
    subpage = request.args.get("subpage", default=1, type=int)
    perpagelimit = request.args.get("perpagelimit", type=int)
    paginated_offers = JobOffer.query.paginate(page=subpage, per_page=perpagelimit)
    return joboffers_schema.dump(paginated_offers)
