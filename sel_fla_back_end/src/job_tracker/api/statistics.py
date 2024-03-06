from contextlib import contextmanager
from datetime import datetime, timedelta

from connexion.problem import problem
from flask import request
from sqlalchemy import and_, delete, func, inspect, select, true

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


@contextmanager
def temporary_timestamps_table():
    r"""Create a temporary table for continuous range of timestamps

    A table is created (if it doesn't already exist) using current
    database context. Table has a single column which should be filled
    with a continuous range of timestamps inside the context create
    by this manager.

    Not data are inserted into the table, the manager just yields
    the table object.
    However after the context is closed all the table rows are removed
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

    class TmpContinuousDatesRange(db.Model):
        __tablename__ = "tmp_continuous_dates_range"
        timestamp = db.Column(db.DateTime, primary_key=True, autoincrement=False)

        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)

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

    start_date : earliest date an offer was collected on
    end_date : latest date an offer was collected on
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
                    func.extract("year", JobOffer.collected),
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
                    func.extract("year", JobOffer.collected),
                    func.extract("month", JobOffer.collected),
                ]

                for first_day in iterate_months(mod_sd, mod_ed):
                    db.session.add(TmpContinuousDatesRange(timestamp=first_day))
            case Interval.DAY:
                mod_sd = start_date.replace(hour=0, minute=0, second=0)
                mod_ed = end_date.replace(hour=23, minute=59, second=59)

                grouping_criteria = [
                    func.extract("year", JobOffer.collected),
                    func.extract("month", JobOffer.collected),
                    func.extract("day", JobOffer.collected),
                ]

                dates_range = [
                    mod_sd + timedelta(days=x)
                    for x in range(0, (mod_ed - mod_sd).days + 1)
                ]
                for date in dates_range:
                    db.session.add(TmpContinuousDatesRange(timestamp=date))

        selection_criteria = [
            JobOffer.collected >= mod_sd,
            JobOffer.collected <= mod_ed,
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

        series = select(TmpContinuousDatesRange.timestamp)
        series_sq = series.subquery()
        stmt = (
            select(
                JobOffer.collected,
                func.count(JobOffer.joboffer_id).label("count"),
            )
            .where(and_(true(), *selection_criteria))
            .group_by(
                *grouping_criteria,
            )
        )
        stmt_sq = stmt.subquery()

        # Show what is going on
        # TODO: Remove when not needed
        print("############# Bare stmt execution #####################")
        for result in db.session.execute(stmt).fetchall():
            print(result)
        print("#######################################################")
        print("+++++++++++++ And this is how generated dates look like ++++++++++")
        for generated_date in db.session.execute(series).fetchall():
            print(generated_date)
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

        comparison_criteria = [
            func.extract("year", stmt_sq.c.collected)
            == func.extract("year", series_sq.c.timestamp)
        ]
        if not binning == Interval.YEAR:
            comparison_criteria.append(
                func.extract("month", stmt_sq.c.collected)
                == func.extract("month", series_sq.c.timestamp)
            )
            if not binning == Interval.MONTH:
                comparison_criteria.append(
                    func.extract("day", stmt_sq.c.collected)
                    == func.extract("day", series_sq.c.timestamp)
                )

        # data_points is a list of rows. Each row is an object that has methods
        # corresponding to the names of "columns" in the select statement.
        # (To "rename the column" and hence the object's method name
        # use .label("str") method).
        # data_points serializer expects returned objects
        # to have .date and .count methods
        joined_query = (
            select(
                series_sq.c.timestamp.label("date"),
                func.coalesce(stmt_sq.c.count, 0).label("count"),
            )
            .outerjoin(stmt_sq, and_(true(), *comparison_criteria))
            .order_by(series_sq.c.timestamp.asc())
        )
        data_points = db.session.execute(joined_query).fetchall()

    # TODO: Remove when not needed
    print("!!!!!!!!!! RESULTS INCOMING !!!!!!!!!!!!!!!!!!!")
    for row in data_points:
        print(f"Date is: {row.date} Count is: {row.count}")
    print("!!!!!!!!!!      THE END     !!!!!!!!!!!!!!!!!!!")
    return data_points


def timedependant():
    # connexion automatically validates date FORMAT based on API specification
    # but casting them here from string to datetime objects.
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
    # will automatically check this against choices allowed in API specification,
    # but casting is done since using enum in makes for cleaner code.
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
    return datapoints_schema.dump(stats)
