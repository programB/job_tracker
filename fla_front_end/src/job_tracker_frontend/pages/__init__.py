from flask import Blueprint

bp = Blueprint("pages", __name__)

from job_tracker_frontend.pages import about, home, offers, status
