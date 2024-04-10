import pytest

from job_tracker.pracujpl_POM import ResultsPage

# Stored copy of the results page in the 'data' subdirectory
# to be served by http server spun up by the local_http_server fixture
file_to_serve = "resultspage.html"
# special properties of the server object needed in tests
# and known to be valid for the stored copy of the results page.
special_properties = {"tot_no_of_subpages": 3}


@pytest.fixture
def std_results_page(app_context, selenium_driver, local_http_server):
    selenium_driver.get(local_http_server.url)
    yield ResultsPage(
        selenium_driver,
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


def test_should_create_ResultPage_object(app_context, std_results_page):
    """
    GIVEN a selenium driver object
    WHEN ResultsPage object is created
    THEN check the object was created
    """
    assert std_results_page is not None


def test_should_check_tot_number_of_subpages(app_context, std_results_page):
    assert std_results_page.tot_no_of_subpages >= 2


def test_should_check_only_valid_offers_are_collected(app_context, std_results_page):
    offers = std_results_page.subpage_offers
    assert len(offers) != 0
    for offer in std_results_page.subpage_offers:
        assert offer.is_valid_offer


def test_should_check_essential_params_of_all_offers_are_not_empty(app_context, std_results_page):
    for offer in std_results_page.subpage_offers:
        assert offer.id != 0
        assert offer.title != ""
        assert offer.company_name != ""
        assert offer.job_level != ""
        assert offer.contract_type != ""
