"""Fixtures implicitly auto-imported by integration tests.
These are only really needed by the POM tests but are located at this level
in order to run pytest like: 'pytest test/integration'
without having to specify more detailed path.
"""

# pass --setup-show option to pytest to see the setup and teardown steps
import pytest
from selenium import webdriver

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


def pytest_addoption(parser):
    parser.addoption(
        "--selenium-url",
        help="Url of the Selenium server eg. http://127.0.0.1 \
Use --selenium-port to set port. \
If not passed local webdriver will be used.",
    )

    parser.addoption(
        "--selenium-port",
        help="Port number of the Selenium server, if this option \
is not passed default value 4444 will be used.",
    )

    parser.addoption(
        "--http-test-server-url",
        help="Url of the test http server eg. http://127.0.0.1 \
Use --test-http-server-port to set port. \
If not passed server will bind to 127.0.0.1:8000",
    )

    parser.addoption(
        "--http-test-server-port",
        help="Port number of the test http server, if this option \
is not passed default value 8000 will be used.",
    )


@pytest.fixture(scope="session")
def SELENIUM_URL(request):
    return request.config.getoption("--selenium-url")


@pytest.fixture(scope="session")
def SELENIUM_PORT(request):
    return request.config.getoption("--selenium-port")


@pytest.fixture(scope="session")
def http_test_server_url(request):
    return request.config.getoption("--http-test-server-url")


@pytest.fixture(scope="session")
def http_test_server_port(request):
    return request.config.getoption("--http-test-server-port")


# function scope is the default
# but stating it here explicitly for clarity
@pytest.fixture(scope="function")
def selenium_driver(SELENIUM_URL: str | None, SELENIUM_PORT="4444"):
    # Setup browser driver
    # (with the scope='function' this step is performed
    #  BEFORE EACH test...)

    custom_options = webdriver.ChromeOptions()
    # custom_options.add_argument('--headless')

    if SELENIUM_URL:
        # WARNING: /wd/hub path is deprecated
        # driver = webdriver.Remote("http://selenium:4444/wd/hub")

        # WARNING: command_executor path MUST NOT end with a slash.
        #          "http://127.0.0.1:4444/" is wrong and should be
        #          "http://127.0.0.1:4444"  instead.
        #          Adding trailing slash leads to errors like eg.
        #          "selenium.common.exceptions.WebDriverException: \
        #           Message: Unable to find handler for (POST) //session"
        # driver = webdriver.Remote(
        #     "http://selenium:4444/",
        #     options=options,
        # )

        driver = webdriver.Remote(
            command_executor=SELENIUM_URL + ":" + SELENIUM_PORT,
            options=custom_options,
        )
    else:
        # Use local driver (local browser)
        # if no Selenium server url was given
        driver = webdriver.Chrome(options=custom_options)

    yield driver  # yield control to the test function

    # Teardown after test function returns
    # (...and this one AFTER EACH test)
    driver.quit()
