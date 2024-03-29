from flask import render_template

from job_tracker_frontend.pages import bp


@bp.route("/about")
def about():
    return render_template("pages/about.html")
