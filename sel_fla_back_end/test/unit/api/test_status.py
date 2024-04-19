import json
import os
import tempfile
import unittest.mock

import pytest

from job_tracker import create_app
from job_tracker.config import BaseConfig
from job_tracker.extensions import scheduler


@pytest.fixture
def connexion_app_instance():
    """Create and configure a new app instance for each test."""

    # Create a temporary file for storing sqlite database.
    # Since this fixture is being run before every test,
    # this will ensure every test runs in isolation with
    # its own, fresh copy of the database.
    db_fd, db_fpath = tempfile.mkstemp(prefix="tmp_db_", suffix=".db")
    # print(f"temporary database file is at: {db_fpath}")

    # Create the app with a test configuration.
    class TestConfig(BaseConfig):
        TESTING = True
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_fpath}"

    conxn_app = create_app(custom_config=TestConfig)

    # This only exists because app factory starts the scheduler
    # probably it should be started externally based environment variables
    jobs = scheduler.get_jobs()
    for job in jobs:
        job.remove()

    # Get the underlying flask app from the connexion app instance.
    # wrapped_flask_app = conxn_app.app

    yield conxn_app

    # After the test close and remove the db file.
    os.close(db_fd)
    os.remove(db_fpath)
    # This only exists because app factory starts the scheduler
    # probably it should be started externally based environment variables
    scheduler.shutdown(wait=False)


@pytest.fixture
def flask_http_test_client(connexion_app_instance):
    """Returns a test client for the app."""
    return connexion_app_instance.test_client()


@pytest.mark.parametrize(
    "db_h, sel_h",
    [
        ("fake database status", "fake selenium status"),
        (True, True),
        (False, False),
        (True, False),
        (False, True),
    ],
)
def test_should_get_good_answer_from_health_endpoint(
    flask_http_test_client, db_h, sel_h
):
    # Given
    with unittest.mock.patch(
        "job_tracker.api.status.get_database_status"
    ) as mock_db_h, unittest.mock.patch(
        "job_tracker.api.status.get_selenium_service_status"
    ) as mock_selenium_h:
        mock_db_h.return_value = db_h
        mock_selenium_h.return_value = sel_h
        # When
        response = flask_http_test_client.get("/api/health")

    # Then
    assert response.status_code == 200
    assert json.loads(response.text) == {
        "is_selenium_service_healthy": sel_h,
        "is_database_online": db_h,
    }
