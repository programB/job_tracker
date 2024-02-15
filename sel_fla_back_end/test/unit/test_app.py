import unittest.mock

import pytest
from connexion import FlaskApp
from connexion.jsonifier import json

from job_tracker.app import create_app


def test_app_object_creation():
    app = create_app()
    assert isinstance(app, FlaskApp)


@pytest.fixture
def flask_http_test_client():
    tc = create_app().test_client()
    yield tc


@unittest.mock.patch("job_tracker.api.mydb.db_get_server_health")
def test_should_get_good_answer_from_health_endpoint(
    mocked_health_getter, flask_http_test_client
):
    # Given
    fake_health_data = {
        "is_selenium_grid_healthy": "of course it is",
        "is_database_online": "well, .... not quite yet",
    }
    mocked_health_getter.return_value = fake_health_data

    # When
    response = flask_http_test_client.get("/api/health")

    # Then
    assert response.status_code == 200
    assert json.loads(response.text) == fake_health_data


@unittest.mock.patch("job_tracker.api.mydb.db_get_tags")
def test_should_get_good_answer_from_tags_endpoint(
    mocked_tags_getter, flask_http_test_client
):
    # Given
    fake_tags = ["tag1", "tag2", "tag3"]
    mocked_tags_getter.return_value = fake_tags

    # When
    response = flask_http_test_client.get("/api/tags")

    # Then
    assert response.status_code == 200
    assert json.loads(response.text) == fake_tags


@pytest.mark.xfail
def test_should_get_500error_from_tags_endpoint_if_server_not_healthy():
    assert False


@unittest.mock.patch("job_tracker.api.mydb.db_get_offers")
def test_should_get_good_answer_from_offers_endpoint(
    mocked_offers_getter, flask_http_test_client
):
    # Given
    fake_offers = [
        {"id": 0, "fake_field": "fake_val"},
        {"id": 1, "fake_field": "fake_val"},
    ]
    mocked_offers_getter.return_value = fake_offers
    request_params = {"perpagelimit": 10, "subpage": 1}

    # When
    response = flask_http_test_client.get("/api/offers", params=request_params)

    # Then
    assert response.status_code == 200
    assert json.loads(response.text) == fake_offers


def test_should_get_400error_from_offers_endpoint_on_missing_params(
    flask_http_test_client,
):
    # Given
    # (missing required parameters)
    invalid_request_params = {}

    # When
    response = flask_http_test_client.get(
        "/api/offers",
        params=invalid_request_params,
    )

    # Then
    assert response.status_code == 400


@pytest.mark.xfail
def test_should_get_500error_from_offers_endpoint_if_server_not_healthy():
    assert False


@unittest.mock.patch("job_tracker.api.mydb.db_get_statistics")
def test_should_get_good_answer_from_statistics_endpoint(
    mocked_stats_getter, flask_http_test_client
):
    # Given
    fake_stats = [
        {"date": "2021-09-01", "count": 1},
        {"date": "2021-09-03", "count": 42},
    ]
    mocked_stats_getter.return_value = fake_stats
    request_params = {
        "start_date": "2021-01-01",
        "end_date": "2021-12-31",
        "tags": ["C", "Jira"],
        "contract_type": ["full time", "part time"],
        "job_mode": "remote",
        "job_level": "senior",
    }

    # When
    response = flask_http_test_client.get("/api/statistics", params=request_params)

    # Then
    assert response.status_code == 200
    assert json.loads(response.text) == fake_stats


def test_should_get_400error_answer_from_statistics_endpoint_on_missing_params(
    flask_http_test_client,
):
    # Given
    # (missing required parameters)
    invalid_request_params = {}

    # When
    response = flask_http_test_client.get(
        "/api/statistics", params=invalid_request_params
    )

    # Then
    assert response.status_code == 400


@pytest.mark.xfail
def test_should_get_500error_from_statistics_endpoint_if_server_not_healthy():
    assert False
