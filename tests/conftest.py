"""Fixtures implicitly auto-imported by every test module"""

import pytest
from selenium import webdriver

# pass --setup-show option to pytest to see the setup and teardown steps


# function scope is the default
# but stating it here explicitly for clarity
@pytest.fixture(scope="function")
def selenium_driver():
    # Setup browser driver
    # (with the scope='function' this step is performed
    #  BEFORE EACH test...)
    driver = webdriver.Chrome()

    yield driver  # yield control to the test function

    # Teardown after testing is completed
    # (...and this one AFTER each test)
    driver.quit()
