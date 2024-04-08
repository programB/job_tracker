from __future__ import annotations

import logging
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import pytest

from job_tracker.pracujpl_POM import PracujplMainPage


@pytest.fixture
def stored_main_page(shared_datadir, http_test_server_url, http_test_server_port):
    """Fixture starts local http server with saved copy of pracuj.pl main page.

    This fixture uses pytest-datadir plugin (its shared_datadir fixture)
    to copy the contents of ./data directory, which contains the saved webpage
    with its assets (scripts, images, stylesheets), to a temporary directory
    removed after test. This way a test can't, even accidentally, change
    these files which would affect other tests.
    This fixture starts a local httpserver running in a separate thread.
    """

    # server_address = "localhost"
    # bind to 0.0.0.0 so the server will be visible inside docker network
    # by the name given to the container running this test.
    bind_address = "0.0.0.0"
    server_port = 8000 if not http_test_server_port else int(http_test_server_port)

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=shared_datadir, **kwargs)

    class LocalServer(threading.Thread):
        if http_test_server_url:
            url = http_test_server_url + ":" + str(server_port) + "/mainpage.html"
        else:
            url = "http://" + bind_address + ":" + str(server_port) + "/mainpage.html"

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


@pytest.fixture
def std_main_page(selenium_driver, stored_main_page):
    """Fixture opens test website on the test server.
    It is used by almost all tests except those requiring different
    initial settings in which case the test creates page object itself.
    """
    yield PracujplMainPage(
        selenium_driver,
        url=stored_main_page.url,
        reject_cookies=True,
        visual_mode=False,
        # Test website doesn't have any advertisement popups to close.
        # Setting this to False saves time waiting for those popups
        # to appear on the website.
        attempt_closing_popups=False,
        # By default BaseNavigation derived objects use 5 second wait time
        # when looking for specific tags.
        # PracujplMainPage uses this wait strategy to look for cookie consent
        # overlay to appear on the screen. This is OK for real application but
        # since the test website doesn't have this overlay
        # tests can be sped up by setting the timeout to smaller value
        # (set to 1 second as further decrease doesn't seem to reduce
        # execution time).
        timeout=1.0,
    )


def test_should_create_PracujplMainPage_object(std_main_page):
    assert std_main_page is not None


def test_should_visit_pracujpl_home_on_object_creation(selenium_driver, std_main_page):
    _ = std_main_page
    assert "Praca - Pracuj.pl" in selenium_driver.title


def test_should_check_essential_search_options_are_available(std_main_page):
    search_field = std_main_page.search_field
    category_field = std_main_page.category_field
    location_field = std_main_page.location_field
    assert search_field.is_displayed() and search_field.is_enabled()
    assert category_field.is_displayed() and category_field.is_enabled()
    assert location_field.is_displayed() and location_field.is_enabled()


def test_should_check_distance_field_is_shown_when_requested(std_main_page):
    # _distance_dropdown only gets shown if browser window is maximized.
    # Test should succeed only if the window gets maximized when
    # the property is called and afterwards the dropdown gets found on the page
    assert std_main_page._distance_dropdown.is_displayed()


@pytest.mark.parametrize("reject_param", [True, False])
def test_should_enter_text_into_search_field(
    selenium_driver, stored_main_page, reject_param
):
    non_std_main_page = PracujplMainPage(
        selenium_driver,
        url=stored_main_page.url,
        reject_cookies=reject_param,
        visual_mode=True,
        attempt_closing_popups=False,
    )
    text_to_enter = "Tester"
    non_std_main_page.search_term = text_to_enter
    assert non_std_main_page.search_term.casefold() == text_to_enter.casefold()


def test_should_check_extended_search_options_are_available(
    selenium_driver, std_main_page
):
    # extended controls are only visible if window is maximized
    selenium_driver.maximize_window()
    assert (
        std_main_page.job_level.menu.is_displayed()
        and std_main_page.contract_type.menu.is_displayed()
        and std_main_page.employment_type_menu.menu.is_displayed()
        and std_main_page.job_mode.menu.is_displayed()
    )


def test_should_check_job_levels_can_be_selected(selenium_driver, std_main_page):
    # extended controls are only visible if window is maximized
    selenium_driver.maximize_window()
    #
    levels = [
        "trainee",
        "assistant",
        "junior",
        "mid_regular",
        "senior",
        "expert",
        "manager",
        "director",
        "president",
        "laborer",
    ]
    choice = levels[3]
    std_main_page.job_level.select([choice])

    assert std_main_page.job_level.is_selected(choice)


def test_should_check_contract_types_can_be_selected(selenium_driver, std_main_page):
    # extended controls are only visible if window is maximized
    selenium_driver.maximize_window()
    #
    types = [
        "o_prace",
        "o_dzielo",
        "zlecenie",
        "B2B",
        "o_zastepstwo",
        "agencyjna",
        "o_prace_tymczasowa",
        "praktyki",
    ]
    choice = types[4]
    std_main_page.contract_type.select([choice])

    assert std_main_page.contract_type.is_selected(choice)


def test_should_check_employment_types_can_be_selected(selenium_driver, std_main_page):
    # extended controls are only visible if window is maximized
    selenium_driver.maximize_window()
    #
    types = [
        "part_time",
        "temporary",
        "full_time",
    ]
    choice = types[2]
    std_main_page.employment_type = [choice]

    assert std_main_page.employment_type == [choice]


def test_should_check_job_locations_can_be_selected(selenium_driver, std_main_page):
    # extended controls are only visible if window is maximized
    selenium_driver.maximize_window()
    #
    locations = [
        "full_office",
        "hybrid",
        "home_office",
        "mobile",
    ]
    choice = locations[1]
    std_main_page.job_mode.select([choice])

    assert std_main_page.job_mode.is_selected(choice)
