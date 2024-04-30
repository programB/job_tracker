from __future__ import annotations

import datetime
import time

import pytest
from selenium.common import exceptions as SE
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from job_tracker.pracujpl_POM import BaseNavigation

# A simple single page html page in the 'data' subdirectory
# to be served by http server spun up by the local_http_server fixture
file_to_serve = "simple_test_page.html"
# special properties of the server object needed in tests
# and known to be valid for this html file.
special_properties = {
    "title": "Simple test page",
    "locator_of_existing_body_tag": (By.TAG_NAME, "body"),
    "locator_of_existing_p_tag": (By.XPATH, "/html/body/div[1]/p[1]"),
    "locator_of_existing_h2_tag": (By.XPATH, "/html/body/h2[2]"),
    "locator_of_not_existing_tag": (By.TAG_NAME, "not_existing_tag"),
}


@pytest.fixture
def browser(app_context, selenium_driver):
    return BaseNavigation(selenium_driver)


def test_should_visit_an_existing_webpage(app_context, browser, local_http_server):
    browser.visit(local_http_server.url)
    assert browser.driver.title == local_http_server.title


def test_should_fail_to_visit_a_not_existing_webpage(app_context, browser):
    with pytest.raises(ConnectionError):
        browser.visit("https://localhost1")


def test_should_find_an_existing_tag_on_a_webpage(
    app_context, browser, local_http_server
):
    browser.visit(local_http_server.url)
    search_result = browser.find(local_http_server.locator_of_existing_body_tag)
    assert isinstance(search_result, WebElement)


def test_should_find_and_highlight_an_existing_tag_on_a_webpage(
    app_context, browser, local_http_server
):
    browser.visit(local_http_server.url)
    emph_color = "red"
    result = browser.find(
        local_http_server.locator_of_existing_h2_tag, highlight_color=emph_color
    )
    assert isinstance(result, WebElement)
    assert f"background-color: {emph_color}" in (
        result.get_attribute("style") or "style attribute note found"
    )


def test_should_fail_to_find_not_existing_tag_on_a_webpage(
    app_context, browser, local_http_server
):
    browser.visit(local_http_server.url)
    with pytest.raises(SE.NoSuchElementException):
        browser.find(local_http_server.locator_of_not_existing_tag)


def test_should_confirm_visibility_of_displayed_element(
    app_context, browser, local_http_server
):
    browser.visit(local_http_server.url)
    assert browser.is_displayed(local_http_server.locator_of_existing_p_tag) is True


def test_should_fail_to_see_a_non_existing_element(
    app_context, browser, local_http_server
):
    browser.visit(local_http_server.url)
    assert browser.is_displayed(local_http_server.locator_of_not_existing_tag) is False


def test_should_modify_default_timeout(app_context, browser, local_http_server):
    new_timeout = 6

    browser.timeout_sec = new_timeout
    browser.visit(local_http_server.url)
    before = datetime.datetime.now()
    _ = browser.is_displayed(local_http_server.locator_of_not_existing_tag)
    after = datetime.datetime.now()

    assert (after - before).seconds >= new_timeout


def test_should_force_highlighting_of_found_elements(
    app_context, browser, local_http_server
):
    browser.set_visual_mode(True)
    browser.visit(local_http_server.url)
    element = browser.find(local_http_server.locator_of_existing_p_tag)
    element_style = element.get_attribute("style")
    assert "background-color: " in element_style


def test_should_highlight_single_elements_if_visual_mode_is_off(
    app_context, browser, local_http_server
):
    browser.set_visual_mode(False)
    browser.visit(local_http_server.url)

    color_to_apply = "magenta"

    el1 = browser.find(local_http_server.locator_of_existing_p_tag)
    el2 = browser.find(
        local_http_server.locator_of_existing_h2_tag,
        highlight_color=color_to_apply,
    )
    el1_style = el1.get_attribute("style")
    el2_style = el2.get_attribute("style")
    time.sleep(1)
    assert (el1_style == "") and (color_to_apply in el2_style)
