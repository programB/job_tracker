from datetime import datetime, timedelta

earliest_date = datetime(2024, 1, 1)
latatest_date = datetime(2034, 12, 31)
default_start_date = earliest_date
default_end_date = earliest_date + timedelta(days=365)

default_bin = "day"
default_tag = ""
# "Pełny etat" is the only type of offer that should exist
# as this is the only type that the backend searches for
# and collects in the database.
default_contract_type = "Pełny etat"
default_job_mode = ""
default_job_level = ""
