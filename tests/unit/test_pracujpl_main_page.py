# import time

import pytest
from selenium import webdriver
from selenium.common import exceptions as SE

from tester_jobs_auto.pracujpl_POM import PracujplMainPage

temp_skip = False


@pytest.fixture
def selenium_driver():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()


@pytest.mark.skipif(temp_skip, reason="BECAUSE WIP on the LATEST TEST ONLY")
def test_should_create_PracujplMainPage_object(selenium_driver):
    assert PracujplMainPage(selenium_driver) is not None


@pytest.mark.skipif(temp_skip, reason="BECAUSE WIP on the LATEST TEST ONLY")
def test_should_visit_pracujpl_home_on_object_creation(selenium_driver):
    _ = PracujplMainPage(selenium_driver)
    assert "Praca - Pracuj.pl" in selenium_driver.title


@pytest.mark.skipif(temp_skip, reason="BECAUSE WIP on the LATEST TEST ONLY")
def test_should_dismiss_cookie_modal_by_rejecting_cookies_on_object_creation(selenium_driver):
    main_page = PracujplMainPage(selenium_driver, reject_cookies=True)
    with pytest.raises(SE.StaleElementReferenceException):
        assert (
            main_page.overlay_cookie_consent is None or not main_page.overlay_cookie_consent.is_displayed()
        ) and main_page.search_bar_box.is_displayed()


@pytest.mark.skipif(temp_skip, reason="BECAUSE WIP on the LATEST TEST ONLY")
def test_should_dismiss_cookie_modal_by_accepting_cookies_on_object_creation(selenium_driver):
    main_page = PracujplMainPage(selenium_driver, reject_cookies=False)
    with pytest.raises(SE.StaleElementReferenceException):
        assert (
            main_page.overlay_cookie_consent is None or not main_page.overlay_cookie_consent.is_displayed()
        ) and main_page.search_bar_box.is_displayed()


@pytest.mark.skipif(temp_skip, reason="BECAUSE WIP on the LATEST TEST ONLY")
def test_should_check_essential_search_options_are_available(selenium_driver):
    main_page = PracujplMainPage(selenium_driver, reject_cookies=True, visual_mode=True)
    assert main_page.search_field.is_displayed() and main_page.search_field.is_enabled()
    assert main_page.category_field.is_displayed() and main_page.category_field.is_enabled()
    assert main_page.location_field.is_displayed() and main_page.location_field.is_enabled()
    assert main_page.btn_search_submit.is_displayed() and main_page.btn_search_submit.is_enabled()


@pytest.mark.skipif(temp_skip, reason="BECAUSE WIP on the LATEST TEST ONLY")
def test_should_check_distance_field_is_shown_when_window_is_maximized(selenium_driver):
    main_page = PracujplMainPage(selenium_driver, reject_cookies=True)
    selenium_driver.maximize_window()
    assert main_page.distance_field.is_displayed()


@pytest.mark.skipif(temp_skip, reason="BECAUSE WIP on the LATEST TEST ONLY")
@pytest.mark.parametrize("reject_cookies", [True, False])
def test_should_wait_untill_cookie_consent_modal_is_gone_before_returning(selenium_driver, reject_cookies):
    main_page = PracujplMainPage(
        selenium_driver,
        reject_cookies=reject_cookies,
        visual_mode=True,
    )
    text_to_enter = "Tester"
    search_field = main_page.search_field
    search_field.send_keys(text_to_enter)
    assert search_field.is_displayed() and search_field.get_attribute("value") == text_to_enter


def test_should_check_extended_search_options_are_available(selenium_driver):
    main_page = PracujplMainPage(selenium_driver, reject_cookies=True, visual_mode=False)
    # extended controls are only visible if window is maximized
    selenium_driver.maximize_window()
    assert (
        main_page.job_level.menu.is_displayed()
        and main_page.contract_type.menu.is_displayed()
        and main_page.employment_type.menu.is_displayed()
        and main_page.job_location.menu.is_displayed()
    )


def test_should_check_job_levels_can_be_selected(selenium_driver):
    main_page = PracujplMainPage(selenium_driver, reject_cookies=True, visual_mode=False)
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
    main_page.job_level.select([choice])

    assert main_page.job_level.is_selected(choice)


def test_should_check_contract_types_can_be_selected(selenium_driver):
    main_page = PracujplMainPage(selenium_driver, reject_cookies=True, visual_mode=False)
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
    main_page.contract_type.select([choice])

    assert main_page.contract_type.is_selected(choice)


def test_should_check_employment_types_can_be_selected(selenium_driver):
    main_page = PracujplMainPage(selenium_driver, reject_cookies=True, visual_mode=False)
    # extended controls are only visible if window is maximized
    selenium_driver.maximize_window()
    #
    types = [
        "part_time",
        "temporary",
        "full_time",
    ]
    choice = types[2]
    main_page.employment_type.select([choice])

    assert main_page.employment_type.is_selected(choice)


def test_should_check_job_locations_can_be_selected(selenium_driver):
    main_page = PracujplMainPage(selenium_driver, reject_cookies=True, visual_mode=False)
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
    main_page.job_location.select([choice])

    assert main_page.job_location.is_selected(choice)
