from flask import Blueprint, render_template

bp = Blueprint("pages", __name__)


@bp.route("/")  # home() defines a view (Flask terminology)
def home():
    return render_template("pages/home.html")


@bp.route("/about")
def about():
    return render_template("pages/about.html")
