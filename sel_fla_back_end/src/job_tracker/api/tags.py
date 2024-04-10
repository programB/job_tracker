from connexion.problem import problem
from flask import current_app
from sqlalchemy import exc

from job_tracker.models import Tag

# from job_tracker.models import Tag, tags_schema


def get_all():
    try:
        tags = Tag.query.all()
    except exc.OperationalError:
        current_app.logger.exception(
            ("Failed to connect to the database while trying query for tags")
        )
        return problem(
            status=500, title="database offline", detail="Check server health"
        )
    else:
        # return tags_schema.dump(tags)
        return [tag.name for tag in tags]
