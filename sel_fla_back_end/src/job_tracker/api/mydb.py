def db_get_server_health():
    return {
        "is_selenium_grid_healthy": False,
        "is_database_online": True,
    }


def db_get_tags():
    return ["all", "tags", "to", "be", "returned", "here"]


def db_get_offers():
    offer1 = {
        "id": 1,
        "title": "offer1",
        "tags": ["tag1", "tag2"],
        "posted": "2020-01-01",
        "collected": "2020-01-02",
        "contract_type": "full time",
        "job_mode": "remote",
    }
    offer2 = {
        "id": 2,
        "title": "offer2",
        "tags": ["tag3", "tag4"],
        "posted": "2021-08-08",
        "collected": "2021-09-09",
        "contract_type": "part time",
        "job_mode": "on site",
    }
    return [offer1, offer2]


def db_get_statistics():
    dp1 = {"date": "2020-01-01", "count": 10}
    dp2 = {"date": "2020-01-02", "count": 8}
    return [dp1, dp2]
