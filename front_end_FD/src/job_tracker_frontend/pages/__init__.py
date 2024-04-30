from flask import Blueprint

bp = Blueprint("pages", __name__)

from job_tracker_frontend.pages import home, offers, status

# Statistics page is provided by
# the statistics_dash sub module
from job_tracker_frontend.pages.statistics_dash import init_dash_app
