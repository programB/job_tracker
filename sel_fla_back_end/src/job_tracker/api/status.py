from . import mydb


def health():
    return mydb.db_get_server_health()
