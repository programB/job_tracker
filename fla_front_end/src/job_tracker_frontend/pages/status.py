from flask import render_template

from job_tracker_frontend.pages import bp


@bp.route("/status")
def status():
    return render_template("pages/status.html")
