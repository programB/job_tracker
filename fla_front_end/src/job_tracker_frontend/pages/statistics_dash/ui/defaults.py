from datetime import datetime, timedelta

earliest_date = datetime(2024, 1, 1)
latatest_date = datetime(2034, 12, 31)
default_start_date = earliest_date
default_end_date = earliest_date + timedelta(days=365)

default_bin = "day"
default_tag = ""
default_contract_type = ""
default_job_mode = ""
default_job_level = ""
