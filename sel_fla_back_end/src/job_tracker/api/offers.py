from . import mydb


def get_all():
    offers = mydb.db_get_offers()
    return offers
