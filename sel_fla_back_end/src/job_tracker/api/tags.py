import logging

from connexion.problem import problem
from sqlalchemy import exc

from job_tracker.models import Tag

# from job_tracker.models import Tag, tags_schema

logger = logging.getLogger(__name__)


def get_all():
    try:
        tags = Tag.query.all()
    except exc.OperationalError:
        logger.exception(
            ("Failed to connect to the database while trying query for tags")
        )
        return problem(
            status=500, title="database offline", detail="Check server health"
        )
    else:
        # return tags_schema.dump(tags)
        return [tag.name for tag in tags]
