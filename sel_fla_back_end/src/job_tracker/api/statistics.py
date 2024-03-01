import datetime
from enum import Enum

from connexion.problem import problem
from flask import request
from sqlalchemy import and_, func, select, true

from job_tracker.database import db
from job_tracker.models import JobOffer, datapoints_schema

# Silence litner for lines using func (eg. func.extract or func.count)
# pylint: disable=not-callable


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


def ISO8601_date_type(date: str) -> datetime.datetime:
    ISO8601_date_format = "%Y-%m-%d"
    try:
        return datetime.datetime.strptime(date, ISO8601_date_format)
    except ValueError as e:
        raise ValueError(
            (
                f"input passed ({date}) does not conform to RFC 3339, "
                "it should be: YYYY-MM-DD"
            )
        ) from e


def calculate_stats(
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    binning: Interval,
    tags: list[str] | None = None,
    contract_type: str | None = None,
    job_mode: str | None = None,
    job_level: str | None = None,
):
    """Counts offers meeting given criteria in specified time bins.

    Parameters
    ----------
    tags : only include offers having ALL of the listed tags.
    contract_type : only include offers with given contract type
    job_mode : only include offers with given job mode
    job_level : only include offers with given job level

    start_date : earliest date an offer was collected on
    end_date : latest date an offer was collected on
    binning : bin matching offer by either day, month or year

    Returns
    -------
    [(datetime.date, int)]
    """

    def last_day_of_month(any_date: datetime.datetime) -> datetime.datetime:
        # The day 28 exists in every month. 4 days later, it's always next month.
        date_in_next_month = any_date.replace(day=28) + datetime.timedelta(days=4)
        # Subtracting the number of the 'new' current day brings us back
        # to the last day of the previous month.
        return date_in_next_month - datetime.timedelta(days=date_in_next_month.day)

    # Expand date and time criteria based on requested binning method
    # ignoring pieces of information in the sd and ed datetime objects passed.
    match binning:
        # FIXME:The query should return all bins in requested range
        #       with 0 if no offers match the criteria for a bin,
        #       now it only returns bins that DO CONTAIN SOME offers
        case Interval.YEAR:
            sd = start_date.replace(month=1, day=1).replace(hour=0, minute=0, second=0)
            ed = end_date.replace(month=12, day=31).replace(
                hour=23, minute=59, second=59
            )
            grouping_criteria = [
                func.extract("year", JobOffer.collected),
            ]
        case Interval.MONTH:
            sd = start_date.replace(day=1).replace(hour=0, minute=0, second=0)
            ed = last_day_of_month(end_date).replace(hour=23, minute=59, second=59)
            grouping_criteria = [
                func.extract("year", JobOffer.collected),
                func.extract("month", JobOffer.collected),
            ]
        case Interval.DAY:
            sd = start_date.replace(hour=0, minute=0, second=0)
            ed = end_date.replace(hour=23, minute=59, second=59)
            grouping_criteria = [
                func.extract("year", JobOffer.collected),
                func.extract("month", JobOffer.collected),
                func.extract("day", JobOffer.collected),
            ]

    selection_criteria = [
        JobOffer.collected >= sd,
        JobOffer.collected <= ed,
    ]
    if contract_type is not None:
        selection_criteria.append(JobOffer.contracttype == contract_type)
    if job_mode is not None:
        selection_criteria.append(JobOffer.jobmode == job_mode)
    if job_level is not None:
        selection_criteria.append(JobOffer.joblevel == job_level)
    # if tags is not None:
    #     TODO: This doesn't work
    #     selection_criteria.append("Python" == any_(JobOffer.tags))

    # data_points is a list of rows. Each row is an object that has methods
    # corresponding to the names of "columns" in the select statement, in
    # this case it will be row.collected and row.count.
    # To "rename the column" (and hence the object's method name)
    # use .label("str") method. (for "date" this will result in existence of
    # row.date instead of row.collected)
    stmt = (
        select(
            JobOffer.collected.label("date"),
            func.count(JobOffer.joboffer_id),
        )
        .where(and_(true(), *selection_criteria))
        .group_by(
            *grouping_criteria,
        )
        .order_by(JobOffer.collected.asc())
    )
    data_points = db.session.execute(stmt).fetchall()
    return data_points


def condition_and_serialize(stats, interval: Interval) -> list:
    # This function is a dirty hack to condition the
    # dates returned by the database based on binning.
    #
    # stats is a list, and its member objects methods must be the same
    # as those of the datapoints_schema in order for dump to work.
    # (eg. datapt.date and datapt.count)
    answer_list = datapoints_schema.dump(stats)
    match interval:
        case Interval.YEAR:
            for dp in answer_list:
                date_items = dp["date"].split("-")
                date_items[1] = "01"  # set month to Jan
                date_items[2] = "01"  # set day to 1st
                dp["date"] = "-".join(date_items)
        case Interval.MONTH:
            for dp in answer_list:
                date_items = dp["date"].split("-")
                date_items[2] = "01"  # set day to 1st
                dp["date"] = "-".join(date_items)
        case Interval.DAY:
            pass
    return answer_list


def timedependant():
    # connexion automatically validates date FORMAT based on API specification
    # but casting them here to datetime objects.
    start_date = request.args.get("start_date", type=ISO8601_date_type)
    # connexion will not validate date CORRECTNESS (eg. it will accept 2023-09-44)
    if start_date is None:
        return problem(status=400, title="Bad request", detail="invalid start_date")
    end_date = request.args.get("end_date", type=ISO8601_date_type)
    if end_date is None:
        return problem(status=400, title="Bad request", detail="invalid end_date")
    if end_date < start_date:
        return problem(
            status=400, title="Bad request", detail="end_date earlier than start_date"
        )
    # There is no need to validate binning type since connexion
    # will automatically check this against the specified enum - this casting
    # is done for the fun of it.
    binning = request.args.get("binning", type=interval_type)
    if binning is None:
        return problem(
            title="Bad request", detail="invalid or missing binning", status=400
        )
    tags = request.args.getlist("tags", type=str)
    contract_type = request.args.get("contract_type", type=str)
    job_mode = request.args.get("job_mode", type=str)
    job_level = request.args.get("job_level", type=str)

    stats = calculate_stats(
        start_date, end_date, binning, tags, contract_type, job_mode, job_level
    )
    return condition_and_serialize(stats, interval=binning)
