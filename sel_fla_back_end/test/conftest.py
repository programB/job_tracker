"""Fixtures implicitly auto-imported by every test module"""

import pytest
from selenium import webdriver

# pass --setup-show option to pytest to see the setup and teardown steps


def pytest_addoption(parser):
    parser.addoption(
        "--selenium-grid-url",
        help="Url of the Selenium Grid server eg. http://127.0.0.1 \
Use --selenium-grid-port to set port. \
If not passed local webdriver will be used.",
    )

    parser.addoption(
        "--selenium-grid-port",
        help="Port number of the Selenium Grid server, if this option \
is not passed default value 4444 will be used.",
    )


@pytest.fixture(scope="session")
def selenium_grid_url(request):
    return request.config.getoption("--selenium-grid-url")


@pytest.fixture(scope="session")
def selenium_grid_port(request):
    return request.config.getoption("--selenium-grid-port")


# function scope is the default
# but stating it here explicitly for clarity
@pytest.fixture(scope="function")
def selenium_driver(selenium_grid_url, selenium_grid_port):
    # Setup browser driver
    # (with the scope='function' this step is performed
    #  BEFORE EACH test...)

    if selenium_grid_url:
        port = selenium_grid_port if selenium_grid_port else "4444"

        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')

        # WARNING: /wd/hub path is deprecated
        # driver = webdriver.Remote("http://chromeindocker:4444/wd/hub")

        # WARNING: command_executor path MUST NOT end with a slash.
        #          "http://127.0.0.1:4444/" is wrong and should be
        #          "http://127.0.0.1:4444"  instead.
        #          Adding trailing slash leads to errors like eg.
        #          "selenium.common.exceptions.WebDriverException: \
        #           Message: Unable to find handler for (POST) //session"
        # driver = webdriver.Remote("http://chromeindocker:4444/", options=options)

        driver = webdriver.Remote(
            command_executor=selenium_grid_url + ":" + port,
            options=options,
        )
    else:
        # Use local driver (local browser)
        # if no Selenium Grid server url was given
        driver = webdriver.Chrome()

    yield driver  # yield control to the test function

    # Teardown after test function returns
    # (...and this one AFTER EACH test)
    driver.quit()
