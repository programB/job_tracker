from __future__ import annotations

import datetime
import logging
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import pytest
from selenium.common import exceptions as SE
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from job_tracker.pracujpl_POM import BaseNavigation


@pytest.fixture
def browser(selenium_driver):
    return BaseNavigation(selenium_driver)


@pytest.fixture
def sample_website(shared_datadir, http_test_server_url, http_test_server_port):
    """Fixture starts local http server with saved copy of pracuj.pl main page.

    This fixture uses pytest-datadir plugin (its shared_datadir fixture)
    to copy the contents of ./data directory (which must exist),
    to a temporary directory removed after test.
    This way a test can't, even accidentally, change
    these files which would affect other tests.
    Before each test a payload html is copied to this temporary dir as a file.
    This fixture starts a local httpserver running in a separate thread.
    """

    # server_address = "localhost"
    # bind to 0.0.0.0 so the server will be visible inside docker network
    # by the name given to the container running this test.
    bind_address = "0.0.0.0"
    server_port = 8000 if not http_test_server_port else int(http_test_server_port)

    html_filename = "index.html"
    page_title = "A test website"
    html_payload = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
      <title>{page_title}</title>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body>
      <h1>Main Section</h1>
      Nothing interesting here
      <h2>Subsection 1</h2>
      <div>
          <p>First paragraph of section 1</p>
          <p>Second paragraph of section 1</p>
      </div>
      <h2>Subsection 2</h2>
      <div>
          <p>First paragraph of section 2</p>
          <p>Second paragraph of section 2</p>
      </div>
    </body>
    </html>
    """
    with open(shared_datadir.joinpath(html_filename), "w", encoding="UTF-8") as f:
        f.write(html_payload)

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=shared_datadir, **kwargs)

    class LocalServer(threading.Thread):
        def __init__(self, *args, title=page_title, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.title = title
            self.locator_of_existing_body_tag = (By.TAG_NAME, "body")
            self.locator_of_existing_p_tag = (By.XPATH, "/html/body/div[1]/p[1]")
            self.locator_of_existing_h2_tag = (By.XPATH, "/html/body/h2[2]")
            self.locator_of_not_existing_tag = (By.TAG_NAME, "not_existing_tag")

        if http_test_server_url:
            url = http_test_server_url + ":" + str(server_port) + "/" + html_filename
        else:
            url = (
                "http://" + bind_address + ":" + str(server_port) + "/" + html_filename
            )

        def run(self):
            self.server = ThreadingHTTPServer((bind_address, server_port), Handler)
            self.server.serve_forever()

        def stop(self):
            self.server.shutdown()

    locsrv = LocalServer()
    locsrv.start()
    if locsrv.is_alive():  # technically the thread not the server itself
        logging.info("Local webserver running at: %s:%s", bind_address, server_port)
    else:
        logging.error("Local webserver failed to start !")
    # logging.info("yielding control to the test function")
    # -- setup is done

    yield locsrv

    # -- teardown
    locsrv.stop()
    if not locsrv.is_alive():
        logging.info("Local webserver successfully stopped")
    else:
        logging.error("Local webserver couldn't be stopped !")


def test_should_visit_an_existing_webpage(browser, sample_website):
    browser.visit(sample_website.url)
    assert browser.driver.title == sample_website.title


def test_should_fail_to_visit_a_not_existing_webpage(browser):
    with pytest.raises(ConnectionError):
        browser.visit("https://localhost1")


def test_should_find_an_existing_tag_on_a_webpage(browser, sample_website):
    browser.visit(sample_website.url)
    search_result = browser.find(sample_website.locator_of_existing_body_tag)
    assert isinstance(search_result, WebElement)


def test_should_find_and_highlight_an_existing_tag_on_a_webpage(
    browser, sample_website
):
    browser.visit(sample_website.url)
    emph_color = "red"
    result = browser.find(
        sample_website.locator_of_existing_h2_tag, highlight_color=emph_color
    )
    assert isinstance(result, WebElement)
    assert f"background-color: {emph_color}" in result.get_attribute("style")


def test_should_fail_to_find_not_existing_tag_on_a_webpage(browser, sample_website):
    browser.visit(sample_website.url)
    with pytest.raises(SE.NoSuchElementException):
        browser.find(sample_website.locator_of_not_existing_tag)


def test_should_confirm_visibility_of_displayed_element(browser, sample_website):
    browser.visit(sample_website.url)
    assert browser.is_displayed(sample_website.locator_of_existing_p_tag) is True


def test_should_fail_to_see_a_non_existing_element(browser, sample_website):
    browser.visit(sample_website.url)
    assert browser.is_displayed(sample_website.locator_of_not_existing_tag) is False


def test_should_modify_default_timeout(browser, sample_website):
    new_timeout = 6

    browser.timeout_sec = new_timeout
    browser.visit(sample_website.url)
    before = datetime.datetime.now()
    _ = browser.is_displayed(sample_website.locator_of_not_existing_tag)
    after = datetime.datetime.now()

    assert (after - before).seconds >= new_timeout


def test_should_force_highlighting_of_found_elements(browser, sample_website):
    browser.set_visual_mode(True)
    browser.visit(sample_website.url)
    element = browser.find(sample_website.locator_of_existing_p_tag)
    element_style = element.get_attribute("style")
    assert "background-color: " in element_style


def test_should_highlight_single_elements_if_visual_mode_is_off(
    browser, sample_website
):
    browser.set_visual_mode(False)
    browser.visit(sample_website.url)

    color_to_apply = "magenta"

    el1 = browser.find(sample_website.locator_of_existing_p_tag)
    el2 = browser.find(
        sample_website.locator_of_existing_h2_tag,
        highlight_color=color_to_apply,
    )
    el1_style = el1.get_attribute("style")
    el2_style = el2.get_attribute("style")
    time.sleep(1)
    assert (el1_style == "") and (color_to_apply in el2_style)
