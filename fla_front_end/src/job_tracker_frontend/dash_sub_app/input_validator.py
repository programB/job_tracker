from datetime import datetime, timedelta

earliest_date = datetime(2024, 1, 1)
latatest_date = datetime(2034, 12, 31)
default_start_date = earliest_date
default_end_date = earliest_date + timedelta(days=365)

bins = ["day", "month", "year"]
default_bin = "day"

tags = []
default_tag = ""

contract_types = ["full time", "part time", "temporary"]
default_contract_type = ""

job_modes = ["in office", "remote"]
default_job_mode = ""

job_levels = ["junior", "regular", "senior"]
default_job_level = ""
