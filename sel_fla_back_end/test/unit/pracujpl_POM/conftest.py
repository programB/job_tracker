"""Fixtures implicitly auto-imported by unit POM tests."""

import unittest.mock

import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


@pytest.fixture
def mock_driver():
    # driver: WebDriver = unittest.mock.create_autospec(webdriver.Chrome)
    driver: WebDriver = unittest.mock.create_autospec(WebDriver)
    # driver.session_id = "fake_session_id"
    yield driver


@pytest.fixture
def mock_element():
    element = unittest.mock.create_autospec(WebElement)
    yield element


@pytest.mark.skip
def test_mock_driver_fixture(mock_driver):
    assert isinstance(mock_driver, WebDriver)


@pytest.mark.skip
def test_mock_element_fixture(mock_element):
    assert isinstance(mock_element, WebElement)
