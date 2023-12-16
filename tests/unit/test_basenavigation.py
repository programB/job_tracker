import datetime
import time

import pytest
from selenium import webdriver
from selenium.common import exceptions as SE
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from tester_jobs_stats.pracujpl_POM import BaseNavigation

temporary_skip = False


@pytest.fixture
def selenium_driver():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()


@pytest.fixture
def nav_window(selenium_driver):
    return BaseNavigation(selenium_driver)


@pytest.fixture
def existing_tag_on_existing_website():
    website = "https://www.google.com"
    body_tag = (By.TAG_NAME, "body")
    return (body_tag, website)


@pytest.fixture
def non_existing_tag_on_existing_website():
    website = "https://www.google.com"
    non_existing_tag = (By.TAG_NAME, "nonexistinghtmltag")
    return (non_existing_tag, website)


def test_should_create_BaseNavigation(selenium_driver):
    assert BaseNavigation(selenium_driver) is not None


@pytest.mark.parametrize(
    "property",
    [
        "timeout_sec",
    ],
)
def test_should_assure_properties_existance(property):
    assert hasattr(BaseNavigation, property)


@pytest.mark.parametrize(
    "method",
    [
        "visit",
        "find",
        "click",
        "enter_text",
        "is_displayed",
    ],
)
def test_should_assure_methods_existance(method):
    assert hasattr(BaseNavigation, method)
    # Can't do:
    # assert callable(BaseNavigation.visit)
    # directly because method is a str.
    # Doing __dict__[method] istead
    assert callable(BaseNavigation.__dict__[method])


@pytest.mark.skipif(temporary_skip is True, reason="skipping to concentrate on the latest test")
def test_should_visit_a_webpage(nav_window):
    nav_window.visit("https://www.google.com")
    assert "google".casefold() in nav_window.driver.title.casefold()


@pytest.mark.skipif(temporary_skip is True, reason="skipping to concentrate on the latest test")
def test_should_find_an_existing_tag_on_a_webpage(nav_window):
    nav_window.visit("https://www.google.com")
    assert isinstance(nav_window.find((By.TAG_NAME, "body")), WebElement)


@pytest.mark.skipif(temporary_skip is True, reason="skipping to concentrate on the latest test")
@pytest.mark.xfail(reason="This test requires user observing if the tag was highlighted")
def test_should_find_and_highlight_an_existing_tag_on_a_webpage(nav_window):
    nav_window.visit("https://www.google.com")
    assert isinstance(nav_window.find((By.TAG_NAME, "body"), highlight=True), WebElement)


@pytest.mark.skipif(temporary_skip is True, reason="skipping to concentrate on the latest test")
def test_should_fail_to_find_nonexisting_tag_on_a_webpage(
    nav_window,
    non_existing_tag_on_existing_website,
):
    non_existing_tag, website = non_existing_tag_on_existing_website
    nav_window.visit(website)
    with pytest.raises(SE.NoSuchElementException) as not_foud_e:
        nav_window.find(non_existing_tag)


@pytest.mark.skipif(temporary_skip is True, reason="skipping to concentrate on the latest test")
@pytest.mark.xfail(reason="This test requires user observing if button was clicked")
def test_should_click_a_button(nav_window):
    nav_window.visit("https://www.google.com")
    try:
        btn = nav_window.find((By.XPATH, "//div[@id='uMousc']//descendant::button"), highlight=True)
        btn.click()
        time.sleep(2)
    except SE.NoSuchElementException as e:
        raise e


@pytest.mark.skipif(temporary_skip is True, reason="skipping to concentrate on the latest test")
def test_should_enter_text_into_filed(nav_window):
    # First make the search field visible by dismising the consent modal window
    # (decline cookies)
    nav_window.visit("https://www.google.com")
    try:
        # It seems 4th button in the cookie consent modal window is always
        # the 'decline all' button
        btn = nav_window.find((By.XPATH, "/descendant::button[4]"), highlight=False)
        btn.click()
        # time.sleep(2)
    except SE.NoSuchElementException as e:
        raise e

    text_to_enter = "Who framed Roger Rabbit"
    try:
        # <textarea jsname="yZiJbe" class="gLFyf" jsaction="paste:puy29d;" id="APjFqb" maxlength="2048" name="q" rows="1" aria-activedescendant="" aria-autocomplete="both" aria-controls="Alh6id" aria-expanded="false" aria-haspopup="both" aria-owns="Alh6id" autocapitalize="off" autocomplete="off" autocorrect="off" autofocus="" role="combobox" spellcheck="false" title="Szukaj" type="search" value="" aria-label="Szukaj" data-ved="0ahUKEwjKxZaypZSDAxUEQ_EDHW2TAs0Q39UDCAQ"></textarea>
        search_f = nav_window.find((By.XPATH, "//textarea[@type='search']"))
        nav_window.enter_text(search_f, text_to_enter)
        time.sleep(2)
    except SE.NoSuchElementException as e:
        raise e
    else:
        assert search_f.get_attribute("value") == text_to_enter


@pytest.mark.skipif(temporary_skip is True, reason="skipping to concentrate on the latest test")
def test_should_confirm_visibility_of_displayed_element(
    nav_window,
    existing_tag_on_existing_website,
):
    existing_tag, website = existing_tag_on_existing_website
    nav_window.visit(website)

    assert nav_window.is_displayed(existing_tag) is True


@pytest.mark.skipif(temporary_skip is True, reason="skipping to concentrate on the latest test")
def test_should_fail_to_see_a_non_existing_element(
    nav_window,
    non_existing_tag_on_existing_website,
):
    non_existing_tag, website = non_existing_tag_on_existing_website
    nav_window.visit(website)

    assert nav_window.is_displayed(non_existing_tag) is False


def test_should_modify_default_timeout(
    nav_window,
    non_existing_tag_on_existing_website,
):
    non_existing_tag, website = non_existing_tag_on_existing_website
    new_timeout = 10

    nav_window.timeout_sec = new_timeout
    nav_window.visit(website)
    before = datetime.datetime.now()
    _ = nav_window.is_displayed(non_existing_tag)
    after = datetime.datetime.now()

    assert (after - before).seconds >= new_timeout
