import pytest

from job_tracker.pracujpl_POM import PracujplMainPage


def test_should_create_PracujplMainPage_object(selenium_driver):
    assert PracujplMainPage(selenium_driver) is not None


def test_should_visit_pracujpl_home_on_object_creation(selenium_driver):
    _ = PracujplMainPage(selenium_driver)
    assert "Praca - Pracuj.pl" in selenium_driver.title


def test_should_check_essential_search_options_are_available(selenium_driver):
    main_page = PracujplMainPage(
        selenium_driver,
        reject_cookies=True,
        visual_mode=True,
    )
    search_field = main_page.search_field
    category_field = main_page.category_field
    location_field = main_page.location_field
    assert search_field.is_displayed() and search_field.is_enabled()
    assert category_field.is_displayed() and category_field.is_enabled()
    assert location_field.is_displayed() and location_field.is_enabled()


def test_should_check_distance_field_is_shown_when_requested(selenium_driver):
    # _distance_dropdown only gets shown if browser window is maximized.
    # Test should succeed only if the window gets maximized when
    # the property is called and afterwards the dropdown gets found on the page
    main_page = PracujplMainPage(selenium_driver, reject_cookies=True)
    assert main_page._distance_dropdown.is_displayed()


@pytest.mark.parametrize("reject_param", [True, False])
def test_should_enter_text_into_search_field(selenium_driver, reject_param):
    main_page = PracujplMainPage(
        selenium_driver,
        reject_cookies=reject_param,
        visual_mode=True,
    )
    text_to_enter = "Tester"
    main_page.search_term = text_to_enter
    assert main_page.search_term.casefold() == text_to_enter.casefold()


def test_should_check_extended_search_options_are_available(selenium_driver):
    main_page = PracujplMainPage(
        selenium_driver,
        reject_cookies=True,
        visual_mode=False,
    )
    # extended controls are only visible if window is maximized
    selenium_driver.maximize_window()
    assert (
        main_page.job_level.menu.is_displayed()
        and main_page.contract_type.menu.is_displayed()
        and main_page.employment_type_menu.menu.is_displayed()
        and main_page.job_mode.menu.is_displayed()
    )


def test_should_check_job_levels_can_be_selected(selenium_driver):
    main_page = PracujplMainPage(
        selenium_driver,
        reject_cookies=True,
        visual_mode=False,
    )
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
    main_page = PracujplMainPage(
        selenium_driver,
        reject_cookies=True,
        visual_mode=False,
    )
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
    main_page = PracujplMainPage(
        selenium_driver,
        reject_cookies=True,
        visual_mode=False,
    )
    # extended controls are only visible if window is maximized
    selenium_driver.maximize_window()
    #
    types = [
        "part_time",
        "temporary",
        "full_time",
    ]
    choice = types[2]
    main_page.employment_type = [choice]

    assert main_page.employment_type == [choice]


def test_should_check_job_locations_can_be_selected(selenium_driver):
    main_page = PracujplMainPage(
        selenium_driver,
        reject_cookies=True,
        visual_mode=False,
    )
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
    main_page.job_mode.select([choice])

    assert main_page.job_mode.is_selected(choice)
