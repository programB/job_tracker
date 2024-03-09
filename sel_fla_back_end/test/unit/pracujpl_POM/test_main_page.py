import unittest.mock
from unittest.mock import create_autospec

import pytest
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait

from job_tracker.pracujpl_POM import PracujplMainPage

WebDriverWait.until = create_autospec(WebDriverWait.until)


@pytest.fixture
def mock_driver():
    driver: WebDriver = unittest.mock.create_autospec(webdriver.Chrome)
    driver.session_id = "fake_session_id"
    return driver


@pytest.fixture
def mock_element():
    element = unittest.mock.create_autospec(WebElement)
    return element


def test_should_create_PracujplMainPage_object(mock_driver):
    assert PracujplMainPage(mock_driver) is not None


def test_should_check_essential_search_options_are_available(mock_driver):
    main_page = PracujplMainPage(
        mock_driver,
        reject_cookies=True,
        visual_mode=True,
    )
    search_field = main_page.search_field
    category_field = main_page.category_field
    location_field = main_page.location_field
    assert search_field.is_displayed() and search_field.is_enabled()
    assert category_field.is_displayed() and category_field.is_enabled()
    assert location_field.is_displayed() and location_field.is_enabled()


def test_should_check_distance_field_is_shown_when_requested(mock_driver):
    # _distance_dropdown only gets shown if browser window is maximized.
    # Test should succeed only if the window gets maximized when
    # the property is called and afterwards the dropdown gets found on the page
    main_page = PracujplMainPage(mock_driver, reject_cookies=True)
    assert main_page._distance_dropdown.is_displayed()