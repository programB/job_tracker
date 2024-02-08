import pytest
from flask import Flask

from job_tracker import create_app


def test_app_object_creation():
    app = create_app()
    assert app is not None
    assert isinstance(app, Flask)


@pytest.fixture
def flask_http_test_client():
    return create_app().test_client()


def test_should_get_answer_from_example_endpoint(flask_http_test_client):
    # Given
    expected_answer = "This is an example answer"

    # When
    response = flask_http_test_client.get("/api/example_endpoint/")

    # Then
    assert response.status_code == 200
    assert response.text == expected_answer
