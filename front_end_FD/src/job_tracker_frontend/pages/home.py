from flask import render_template

from job_tracker_frontend.pages import bp


@bp.route("/")
def home():
    return render_template("pages/home.html")
