from job_tracker.models import Tag

# from job_tracker.models import Tag, tags_schema


def get_all():
    tags = Tag.query.all()
    # return tags_schema.dump(tags)
    return [tag.name for tag in tags]
