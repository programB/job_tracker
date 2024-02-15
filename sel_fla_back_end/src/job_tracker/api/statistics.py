from . import mydb


def timedependant():
    stats = mydb.db_get_statistics()
    return stats
