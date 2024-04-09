import pytest

from job_tracker import create_app
from job_tracker.extensions import scheduler


@pytest.fixture(scope="module")
def app_context():
    """Since some of the functions under test use flask app logger
    this fixture creates an application context.
    Every test/test class which ask for this fixture
    will be executed in this context.
    """
    conxn_app = create_app()
    wrapped_flask_app = conxn_app.app
    scheduler.shutdown(wait=False)
    with wrapped_flask_app.app_context():
        yield
