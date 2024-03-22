from flask import Blueprint, render_template

bp = Blueprint("pages", __name__)


@bp.route("/")
def home():
    return render_template("pages/home.html")


@bp.route("/offers")
def offers():
    return render_template("pages/offers.html")


@bp.route("/status")
def status():
    return render_template("pages/status.html")


@bp.route("/about")
def about():
    return render_template("pages/about.html")
