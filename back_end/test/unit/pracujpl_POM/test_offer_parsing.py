import unittest.mock

import pytest
from selenium.webdriver.support.wait import WebDriverWait

from job_tracker.pracujpl_POM import PracujplMainPage, ResultsPage
from job_tracker.pracujpl_POM.main_page import Distance

# Substitute mock for real module to bypass default
# wait strategy altogether and make calls using the until
# method return immediately.
# This speeds up tests and has the effect of pretending
# that all elements selenium is looking for are present and visible.
# This line:
# WebDriverWait.until = create_autospec(WebDriverWait.until)
# works if tests are called like this:
# pytest test/unit/test_offer_parsing.py
# it doesn't work if tests are called like this:
# pytest test/unit/
#  unittest.mock.InvalidSpecError: Cannot spec a Mock object.
#  [object=<MagicMock spec='function' id='140242334309200'>]
#
# This works in both scenarios
mock_WebDriverWait_until = unittest.mock.Mock()
mock_WebDriverWait_until.mock_add_spec(WebDriverWait.until)
WebDriverWait.until = mock_WebDriverWait_until


@pytest.fixture
def standard_search(mock_driver):
    main_page = PracujplMainPage(mock_driver, reject_cookies=True)

    main_page.search_term = "Tester"
    main_page.employment_type = ["full_time"]
    main_page.location_and_distance = ("Warszawa", Distance.TEN_KM)
    main_page.start_searching()

    yield main_page


def test_should_create_ResultPage_object(app_context, mock_driver):
    """
    GIVEN a selenium driver object
    WHEN ResultsPage object is created
    THEN check the the object was created
    """
    assert ResultsPage(mock_driver) is not None
