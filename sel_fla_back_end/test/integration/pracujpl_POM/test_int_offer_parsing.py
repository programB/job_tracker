import logging
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import pytest

from job_tracker.pracujpl_POM import PracujplMainPage, ResultsPage


@pytest.fixture
def results_webpage(shared_datadir, http_test_server_url, http_test_server_port):
    """Fixture starts local http server with saved copy of pracuj.pl main page.

    This fixture uses pytest-datadir plugin (its shared_datadir fixture)
    to copy the contents of ./data directory, which contais the saved webpage
    with its assets (scripts, images, stylesheets), to a temporary directory
    removed after test. This way a test can't, even accidently, change
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
            url = http_test_server_url + ":" + str(server_port) + "/resultspage.html"
        else:
            url = (
                "http://" + bind_address + ":" + str(server_port) + "/resultspage.html"
            )
        tot_no_of_subpages = 3

        def run(self):
            self.server = ThreadingHTTPServer((bind_address, server_port), Handler)
            self.server.serve_forever()

        def stop(self):
            self.server.shutdown()

    locsrv = LocalServer()
    locsrv.start()
    if locsrv.is_alive():  # technicaly the thread not the server itself
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
def std_main_page(selenium_driver, results_webpage):
    # logging.info("Running standard_search fixture")
    # main_page = PracujplMainPage(selenium_driver, reject_cookies=True)
    # main_page.search_term = "Tester"
    # main_page.employment_type = ["full_time"]
    # main_page.location_and_distance = ("Warszawa", Distance.TEN_KM)
    # main_page.start_searching()

    yield PracujplMainPage(
        selenium_driver,
        url=results_webpage.url,
        reject_cookies=True,
        visual_mode=False,
    )


@pytest.fixture
def std_results(std_main_page):
    yield ResultsPage(std_main_page.driver)


def test_should_create_ResultPage_object(std_results):
    """
    GIVEN a selenium driver object
    WHEN ResultsPage object is created
    THEN check the the object was created
    """
    assert std_results is not None


def test_should_check_tot_number_of_subpages(std_results):
    assert std_results.tot_no_of_subpages >= 2


def test_should_check_offers_list_is_not_empty(std_results):
    assert len(std_results.subpage_offers) != 0


def test_should_check_only_valid_offers_are_collected(std_results):
    for offer in std_results.subpage_offers:
        assert offer.is_valid_offer


def test_should_check_offers_have_not_empty_essential_params(std_results):
    for offer in std_results.subpage_offers:
        assert offer.id != 0
        assert offer.title != ""
        assert offer.company_name != ""
        assert offer.job_level != ""
        assert offer.contract_type != ""


# def test_should_check_navigation_to_desired_subpage(standard_search):
#     results_page = ResultsPage(standard_search.driver)

#     # The search criteria in standard_search fixture are general enough
#     # for the returned number of offers to fill more then 1 subpage,
#     # hence assuming the subpage 2 always exists should be safe.
#     desired_subpage = 2
#     results_page.goto_subpage(desired_subpage)
#     _, cur_subpage_number = results_page.get_current_subpage()

#     assert cur_subpage_number == desired_subpage
