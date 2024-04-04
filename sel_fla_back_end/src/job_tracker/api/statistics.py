import logging
from contextlib import contextmanager
from datetime import datetime, timedelta

from connexion.problem import problem
from flask import request
from sqlalchemy import and_, delete, exc, func, inspect, select, true

from job_tracker.database import db
from job_tracker.models import JobOffer, datapoints_schema

from .date_helpers import (
    Interval,
    ISO8601_date_type,
    interval_type,
    iterate_months,
    last_day_of_month,
)

# Silence litner for lines using func (eg. func.extract or func.count)
# pylint: disable=not-callable

logger = logging.getLogger(__name__)


class TmpContinuousDatesRange(db.Model):
    __tablename__ = "tmp_continuous_dates_range"
    timestamp = db.Column(db.DateTime, primary_key=True, autoincrement=False)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)


@contextmanager
def temporary_timestamps_table():
    r"""Create a temporary table for continuous range of timestamps

    A table is created (if it doesn't already exist) using current
    database context. Table has a single column which should be filled
    with a continuous range of timestamps inside the context created
    by this manager.

    No data are inserted into the table, the manager just yields
    the table object.
    However after the context is closed all rows are removed from the table
    (the table itself is not dropped).

    E.g.::

        with temporary_timestamps_table as TmpContinuousDatesRange:
            # Create data and populate the table
            timestamps_range = [
                start + timedelta(days=x)
                for x in range(0, (start - end).days + 1)
            ]
            for tsp in timestamps_range:
                db.session.add(TmpContinuousDatesRange(timestamp=tsp))

            # Use in a query
            a_query = select(TmpContinuousDatesRange.timestamp)
            timestamps_from_db = db.session.execute(a_query).fetchall()

        for row in timestamps_from_db:
            print(row)
    """

    if not inspect(db.engine).has_table(TmpContinuousDatesRange.__tablename__):
        # Create empty table
        TmpContinuousDatesRange.metadata.create_all(db.engine)

    yield TmpContinuousDatesRange

    # Remove all data from the table when context is closed
    # (the table itself is not removed/dropped).
    db.session.execute(delete(TmpContinuousDatesRange))


def calculate_stats(
    start_date: datetime,
    end_date: datetime,
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
    contract_type : only include offers WITH given contract type
    job_mode : only include offers WITH given job mode
    job_level : only include offers WITH given job level

    start_date : earliest date an offer was posted on
    end_date : latest date an offer was posted on
    binning : bin matching offers by either day, month or year

    Returns
    -------
    [(date, int)]
    """

    with temporary_timestamps_table() as TmpContinuousDatesRange:
        match binning:
            # Expand date range (to full years or months)
            # based on requested binning method,
            # establish grouping criteria for the sql query,
            # fill in the TmpContinuousDatesRange table with timestamps.
            case Interval.YEAR:
                mod_sd = start_date.replace(month=1, day=1, hour=0, minute=0, second=0)
                mod_ed = end_date.replace(
                    month=12, day=31, hour=23, minute=59, second=59
                )

                grouping_criteria = [
                    func.extract("year", JobOffer.posted),
                ]

                years = [y for y in range(mod_sd.year, mod_ed.year + 1, 1)]
                for year in years:
                    db.session.add(
                        TmpContinuousDatesRange(
                            timestamp=datetime(year, month=1, day=1)
                        )
                    )
            case Interval.MONTH:
                mod_sd = start_date.replace(day=1, hour=0, minute=0, second=0)
                mod_ed = last_day_of_month(end_date).replace(
                    hour=23, minute=59, second=59
                )

                grouping_criteria = [
                    func.extract("year", JobOffer.posted),
                    func.extract("month", JobOffer.posted),
                ]

                for first_day in iterate_months(mod_sd, mod_ed):
                    db.session.add(TmpContinuousDatesRange(timestamp=first_day))
            case Interval.DAY:
                mod_sd = start_date.replace(hour=0, minute=0, second=0)
                mod_ed = end_date.replace(hour=23, minute=59, second=59)

                grouping_criteria = [
                    func.extract("year", JobOffer.posted),
                    func.extract("month", JobOffer.posted),
                    func.extract("day", JobOffer.posted),
                ]

                dates_range = [
                    mod_sd + timedelta(days=x)
                    for x in range(0, (mod_ed - mod_sd).days + 1)
                ]
                for date in dates_range:
                    db.session.add(TmpContinuousDatesRange(timestamp=date))

        selection_criteria = [
            JobOffer.posted >= mod_sd,
            JobOffer.posted <= mod_ed,
        ]

        if contract_type is not None:
            selection_criteria.append(JobOffer.contracttype == contract_type)
        if job_mode is not None:
            selection_criteria.append(JobOffer.jobmode == job_mode)
        if job_level is not None:
            # WARNING Job offers have job level description in rather
            #         descriptive form (in Polish or Ukrainian) with
            #         general job level term in English in parentheses but
            #         only for junior/regular/senior positions - there
            #         are some non-standard ones as well. The way this is
            #         handled can be improved once enough offers are
            #         collected, hopefully representing all possible levels.
            #         Additionally some offers advertise job opening at
            #         more then one level (probably subject to evaluation during
            #         an interview). This shows that a table for all job levels
            #         should be added (together with a junction table).
            #         This would allow to add multiple level per offer
            #         (similarly to implementation of 'tag' and
            #          'joboffer_tag' tables).
            #         The 'contains' filter below relaxes the search criteria
            #         and allows to select a level even if multiple are present
            #         and the specific wording is not yet fully known.
            # selection_criteria.append(JobOffer.joblevel == job_level)
            selection_criteria.append(JobOffer.joblevel.contains(job_level))
        # if tags is not None:
        #     TODO: This doesn't work
        #     selection_criteria.append("Python" == any_(JobOffer.tags))

        gen_timestamps = select(TmpContinuousDatesRange.timestamp)
        gen_timestamps_subq = gen_timestamps.subquery()
        not_empty_bins = (
            select(
                JobOffer.posted,
                func.count(JobOffer.joboffer_id).label("count"),
            )
            .where(and_(true(), *selection_criteria))
            .group_by(
                *grouping_criteria,
            )
        )
        not_empty_bins_subq = not_empty_bins.subquery()

        comparison_criteria = [
            func.extract("year", not_empty_bins_subq.c.posted)
            == func.extract("year", gen_timestamps_subq.c.timestamp)
        ]
        if not binning == Interval.YEAR:
            comparison_criteria.append(
                func.extract("month", not_empty_bins_subq.c.posted)
                == func.extract("month", gen_timestamps_subq.c.timestamp)
            )
            if not binning == Interval.MONTH:
                comparison_criteria.append(
                    func.extract("day", not_empty_bins_subq.c.posted)
                    == func.extract("day", gen_timestamps_subq.c.timestamp)
                )

        # data_points is a list of rows. Each row is an object that has methods
        # corresponding to the names of "columns" in the select statement.
        # (To "rename the column" and hence the object's method name
        # use .label("str") method).
        # data_points serializer expects returned objects
        # to have .date and .count methods
        joined_query = (
            select(
                gen_timestamps_subq.c.timestamp.label("date"),
                func.coalesce(not_empty_bins_subq.c.count, 0).label("count"),
            )
            .outerjoin(not_empty_bins_subq, and_(true(), *comparison_criteria))
            .order_by(gen_timestamps_subq.c.timestamp.asc())
        )
        data_points = db.session.execute(joined_query).fetchall()

    return data_points


def timedependant():
    # connexion automatically VALIDATES date FORMAT based on API specification
    # but casting here from string to datetime object for easier handling.
    start_date: datetime | None = request.args.get("start_date", type=ISO8601_date_type)
    # connexion WILL NOT validate date CORRECTNESS (eg. it will accept 2023-09-44)
    if start_date is None:
        return problem(status=400, title="Bad request", detail="invalid start_date")
    end_date: datetime | None = request.args.get("end_date", type=ISO8601_date_type)
    if end_date is None:
        return problem(status=400, title="Bad request", detail="invalid end_date")
    if end_date < start_date:
        return problem(
            status=400, title="Bad request", detail="end_date earlier than start_date"
        )
    # There is no need to validate binning value since connexion
    # will automatically check this against choices allowed in API specification,
    # but casting for easier handling in other functions.
    binning = request.args.get("binning", type=interval_type)
    if binning is None:
        return problem(
            title="Bad request", detail="invalid or missing binning", status=400
        )
    tags = request.args.getlist("tags", type=str)
    contract_type = request.args.get("contract_type", type=str)
    # TODO: job_mode is not yet collected when webpage offers are analysed
    #       see: Advertisement class in results_page module
    # job_mode = request.args.get("job_mode", type=str)
    job_mode = None
    job_level = request.args.get("job_level", type=str)

    try:
        stats = calculate_stats(
            start_date, end_date, binning, tags, contract_type, job_mode, job_level
        )
    except exc.OperationalError:
        logger.exception(
            ("Failed to connect to the database while trying query for statistics")
        )
        return problem(
            status=500, title="database offline", detail="Check server health"
        )
    else:
        return datapoints_schema.dump(stats)
