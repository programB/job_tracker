import pytest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from tester_jobs_auto.pracujpl_POM import PracujplMainPage, ResultsPage

temp_skip = False


@pytest.fixture
def selenium_driver():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()


@pytest.fixture
def standard_search(selenium_driver):
    main_page = PracujplMainPage(selenium_driver, reject_cookies=True)
    main_page.gohome()
    selenium_driver.maximize_window()
    main_page.employment_type.select(["full_time"])
    # time.sleep(1)

    main_page.location_field.send_keys("Warszawa")
    main_page.location_field.send_keys(Keys.ENTER)
    # time.sleep(3)

    main_page.search_field.send_keys("Tester")
    main_page.location_field.send_keys(Keys.ENTER)
    # time.sleep(3)

    submit_btn = main_page.btn_search_submit
    submit_btn.click()
    yield main_page


@pytest.mark.skipif(temp_skip, reason="BECAUSE WIP on the LATEST TEST ONLY")
def test_should_create_ResultPage_object(selenium_driver):
    assert ResultsPage(selenium_driver) is not None


@pytest.mark.skipif(temp_skip, reason="BECAUSE WIP on the LATEST TEST ONLY")
def test_should_check_tot_number_of_subpages(standard_search):
    results_page = ResultsPage(standard_search.driver)

    # The search criteria in standard_search fixture are general enough
    # for the returned number of offers to fill more then 1 subpage,
    # hence assuming the subpage 2 always exists should be safe.
    assert results_page.tot_no_of_subpages >= 2


@pytest.mark.skipif(temp_skip, reason="BECAUSE WIP on the LATEST TEST ONLY")
def test_should_check_navigation_to_desired_subpage(standard_search):
    results_page = ResultsPage(standard_search.driver)

    # The search criteria in standard_search fixture are general enough
    # for the returned number of offers to fill more then 1 subpage,
    # hence assuming the subpage 2 always exists should be safe.
    desired_subpage = 2
    results_page.goto_subpage(desired_subpage)
    _, cur_subpage_number = results_page.current_subpage()

    assert cur_subpage_number == desired_subpage


@pytest.mark.skipif(temp_skip, reason="BECAUSE WIP on the LATEST TEST ONLY")
def test_should_check_offers_list_is_not_empty(standard_search):
    results_page = ResultsPage(standard_search.driver)
    assert len(results_page.subpage_offers) != 0


@pytest.mark.skipif(temp_skip, reason="BECAUSE WIP on the LATEST TEST ONLY")
def test_should_check_only_valid_offers_are_collected(standard_search):
    results_page = ResultsPage(standard_search.driver)
    for offer in results_page.subpage_offers:
        assert offer.is_valid_offer


@pytest.mark.skipif(temp_skip, reason="BECAUSE WIP on the LATEST TEST ONLY")
def test_should_check_offers_have_not_empty_essential_params(standard_search):
    results_page = ResultsPage(standard_search.driver)
    for offer in results_page.subpage_offers:
        assert offer.id != 0
        assert offer.title != ""
        assert offer.company_name != ""
        assert offer.job_level != ""
        assert offer.contract_type != ""


@pytest.mark.skipif(temp_skip, reason="BECAUSE WIP on the LATEST TEST ONLY")
def test_should_collect_offers_from_all_subpages(standard_search):
    results_page = ResultsPage(standard_search.driver)
    assert len(results_page.all_offers) != 0
