from . import mydb


def get_all():
    tags = mydb.db_get_tags()
    return tags
