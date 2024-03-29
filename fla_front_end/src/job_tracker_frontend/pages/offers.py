from flask import render_template

from job_tracker_frontend.pages import bp


@bp.route("/offers")
def offers():
    return render_template("pages/offers.html")
