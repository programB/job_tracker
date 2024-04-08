from __future__ import annotations

import pytest

from job_tracker.pracujpl_POM import PracujplMainPage

# Stored copy of the main page in the 'data' subdirectory
# to be serverd by http server spun up by the local_http_server fixture
file_to_serve = "mainpage.html"
# special properties of the server object needed in tests
# and known to be valid for the stored copy of the main page.
special_properties = {}


@pytest.fixture
def std_main_page(selenium_driver, local_http_server):
    """Fixture opens test website on the test server.
    It is used by almost all tests except those requiring different
    initial settings in which case the test creates page object itself.
    """
    yield PracujplMainPage(
        selenium_driver,
        url=local_http_server.url,
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


def test_should_visit_pracujpl_home_on_object_creation(std_main_page):
    assert "Praca - Pracuj.pl" in std_main_page.driver.title


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
    selenium_driver, local_http_server, reject_param
):
    non_std_main_page = PracujplMainPage(
        selenium_driver,
        url=local_http_server.url,
        reject_cookies=reject_param,
        visual_mode=True,
        attempt_closing_popups=False,
    )
    text_to_enter = "Tester"
    non_std_main_page.search_term = text_to_enter
    assert non_std_main_page.search_term.casefold() == text_to_enter.casefold()


def test_should_check_extended_search_options_are_available(std_main_page):
    # extended controls are only visible if window is maximized
    std_main_page.driver.maximize_window()
    assert (
        std_main_page.job_level.menu.is_displayed()
        and std_main_page.contract_type.menu.is_displayed()
        and std_main_page.employment_type_menu.menu.is_displayed()
        and std_main_page.job_mode.menu.is_displayed()
    )


def test_should_check_job_levels_can_be_selected(std_main_page):
    # extended controls are only visible if window is maximized
    std_main_page.driver.maximize_window()
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


def test_should_check_contract_types_can_be_selected(std_main_page):
    # extended controls are only visible if window is maximized
    std_main_page.driver.maximize_window()
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


def test_should_check_employment_types_can_be_selected(std_main_page):
    # extended controls are only visible if window is maximized
    std_main_page.driver.maximize_window()
    #
    types = [
        "part_time",
        "temporary",
        "full_time",
    ]
    choice = types[2]
    std_main_page.employment_type = [choice]

    assert std_main_page.employment_type == [choice]


def test_should_check_job_locations_can_be_selected(std_main_page):
    # extended controls are only visible if window is maximized
    std_main_page.driver.maximize_window()
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
