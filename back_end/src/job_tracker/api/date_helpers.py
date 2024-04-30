from datetime import datetime, timedelta
from enum import Enum


class Interval(Enum):
    """Finite choice of binning periods"""

    DAY = "day"
    MONTH = "month"
    YEAR = "year"


def interval_type(interval: str) -> Interval:
    match interval:
        case "year":
            return Interval.YEAR
        case "month":
            return Interval.MONTH
        case "day":
            return Interval.DAY
        case _:
            raise ValueError(
                f"binning can only be one of: year, month, day - is: {interval}"
            )


def ISO8601_date_type(date: str) -> datetime:
    """Attempts to create datetime object from date

    If date string conforms to the YYYY-MM-DD format (RFC 3339)
    it will be converted to datetime object with time set to 00:00:00

    Parameters
    ----------
    date : str

    Returns
    -------
    datetime

    Raises
    ------
    ValueError
    For date strings not conforming to the YYYY-MM-DD format
    """

    ISO8601_date_format = "%Y-%m-%d"
    try:
        return datetime.strptime(date, ISO8601_date_format)
    except ValueError as e:
        raise ValueError(
            (
                f"input passed ({date}) does not conform to RFC 3339, "
                "it should be: YYYY-MM-DD"
            )
        ) from e


def last_day_of_month(any_date: datetime) -> datetime:
    # Based on
    # https://stackoverflow.com/questions/42950/
    # /get-the-last-day-of-the-month/13565185#13565185
    # The day 28 exists in every month. 4 days later, it's always next month.
    date_in_next_month = any_date.replace(day=28) + timedelta(days=4)
    # Subtracting the number of the 'new' current day brings us back
    # to the last day of the previous month.
    return date_in_next_month - timedelta(days=date_in_next_month.day)


def iterate_months(start_date, end_date):
    """Yields timestamp of 1st day of every month between start and end dates

    Time is always set to 00:00:00
    Range includes both start_date and end_date
    """
    # Based on
    # https://stackoverflow.com/questions/34898525/
    # /generate-list-of-months-between-interval/34899198#34899198
    year = start_date.year
    month = start_date.month
    while True:
        current = datetime(year, month, 1)
        yield current
        if current.month == end_date.month and current.year == end_date.year:
            break
        else:
            month = ((month + 1) % 12) or 12
            if month == 1:
                year += 1
