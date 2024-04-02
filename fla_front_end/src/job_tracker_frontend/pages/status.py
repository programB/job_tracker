from flask import render_template, flash

from job_tracker_frontend.backend_comm.exceptions import (
    APIException,
    BackendNotAvailableException,
)
from job_tracker_frontend.backend_comm.status import get_status
from job_tracker_frontend.pages import bp


@bp.route("/status")
def status():
    try:
        ans = get_status()
    except (AttributeError, APIException, BackendNotAvailableException):
        flash(
            (
                "Failed to retrive backend service status."
            ),
            "error",
        )
        return render_template(
            "pages/status.html",
            selenium_status="Unknown",
            db_status="Unknown",
        )

    selenium_status = "healthy" if ans["is_selenium_grid_healthy"] else "error"
    db_status = "healthy" if ans["is_database_online"] else "error"
    return render_template(
        "pages/status.html",
        selenium_status=selenium_status,
        db_status=db_status,
    )
