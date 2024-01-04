import datetime
import logging
import time

import pytest
from selenium.common import exceptions as SE
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from tester_jobs_auto.pracujpl_POM import BaseNavigation

temporary_skip = False


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


@pytest.mark.skipif(
    temporary_skip is True,
    reason="skipping to concentrate on the latest test",
)
def test_should_create_BaseNavigation(selenium_driver):
    assert BaseNavigation(selenium_driver) is not None


@pytest.mark.skipif(
    temporary_skip is True,
    reason="skipping to concentrate on the latest test",
)
@pytest.mark.parametrize(
    "property",
    [
        "timeout_sec",
    ],
)
def test_should_assure_properties_existence(property):
    assert hasattr(BaseNavigation, property)


@pytest.mark.skipif(
    temporary_skip is True,
    reason="skipping to concentrate on the latest test",
)
@pytest.mark.parametrize(
    "method",
    [
        "visit",
        "find",
        "find_all",
        "is_displayed",
    ],
)
def test_should_assure_methods_existence(method):
    assert hasattr(BaseNavigation, method)
    # Can't do:
    # assert callable(BaseNavigation.visit)
    # directly because method is a str.
    # Doing __dict__[method] istead
    assert callable(BaseNavigation.__dict__[method])


@pytest.mark.skipif(
    temporary_skip is True,
    reason="skipping to concentrate on the latest test",
)
def test_should_visit_an_existing_webpage(nav_window):
    nav_window.visit("https://www.google.com")
    assert "google".casefold() in nav_window.driver.title.casefold()


@pytest.mark.skipif(
    temporary_skip is True,
    reason="skipping to concentrate on the latest test",
)
def test_should_fail_to_visit_a_not_existing_webpage(nav_window):
    with pytest.raises(ConnectionError):
        nav_window.visit("https://www.glubiel.com")


@pytest.mark.skipif(
    temporary_skip is True,
    reason="skipping to concentrate on the latest test",
)
def test_should_find_an_existing_tag_on_a_webpage(nav_window):
    nav_window.visit("https://www.google.com")
    assert isinstance(nav_window.find((By.TAG_NAME, "body")), WebElement)


@pytest.mark.skipif(
    temporary_skip is True,
    reason="skipping to concentrate on the latest test",
)
@pytest.mark.xfail(
    reason="This test requires user observing if the tag was highlighted",
)
def test_should_find_and_highlight_an_existing_tag_on_a_webpage(nav_window):
    nav_window.visit("https://www.google.com")
    emph_color = "red"
    # fmt: off
    logging.warning("If test is successful you should see entire body of "
                    f"the page to be highlighted in '{emph_color.upper()}'")
    # fmt: on
    time.sleep(3)
    assert isinstance(
        nav_window.find((By.TAG_NAME, "body"), highlight_color=emph_color),
        WebElement,
    )


@pytest.mark.skipif(
    temporary_skip is True,
    reason="skipping to concentrate on the latest test",
)
def test_should_fail_to_find_not_existing_tag_on_a_webpage(
    nav_window,
    non_existing_tag_on_existing_website,
):
    non_existing_tag, website = non_existing_tag_on_existing_website
    nav_window.visit(website)
    with pytest.raises(SE.NoSuchElementException):
        nav_window.find(non_existing_tag)


@pytest.mark.skipif(
    temporary_skip is True,
    reason="skipping to concentrate on the latest test",
)
@pytest.mark.xfail(
    reason="This test requires user observing if button was clicked",
)
def test_should_click_a_button(nav_window):
    nav_window.visit("https://www.google.com")
    emph_color = "red"
    try:
        btn = nav_window.find(
            (By.XPATH, "//div[@id='uMousc']//descendant::button"),
            highlight_color=emph_color,
        )
        btn.click()
        # fmt: off
        logging.warning("You should have seen button highlighted in "
                        f"'{emph_color.upper()}' getting clicked")
        # fmt: on
        time.sleep(3)
    except SE.NoSuchElementException as e:
        raise e


@pytest.mark.skipif(
    temporary_skip is True,
    reason="skipping to concentrate on the latest test",
)
def test_should_confirm_visibility_of_displayed_element(
    nav_window,
    existing_tag_on_existing_website,
):
    existing_tag, website = existing_tag_on_existing_website
    nav_window.visit(website)

    assert nav_window.is_displayed(existing_tag) is True


@pytest.mark.skipif(
    temporary_skip is True,
    reason="skipping to concentrate on the latest test",
)
def test_should_fail_to_see_a_non_existing_element(
    nav_window,
    non_existing_tag_on_existing_website,
):
    non_existing_tag, website = non_existing_tag_on_existing_website
    nav_window.visit(website)

    assert nav_window.is_displayed(non_existing_tag) is False


@pytest.mark.skipif(
    temporary_skip is True,
    reason="skipping to concentrate on the latest test",
)
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


def test_should_force_highlighting_of_found_elements(nav_window):
    # should turn highlight to True for all calls of the find method
    nav_window.visit("http://pracuj.pl")
    nav_window.set_visual_mode(True)
    el1 = nav_window.find(
        (
            By.XPATH,
            "//div[@data-test='modal-cookie-bottom-bar']",
        ),
    )
    el2 = nav_window.find(
        (
            By.XPATH,
            "//div[@data-test='modal-cookie-bottom-bar']//descendant::button",
        ),
    )
    style1 = el1.get_attribute("style")
    style2 = el2.get_attribute("style")
    assert "background-color: " in style1 and "background-color: " in style2


def test_should_highlight_single_elements_if_visual_mode_is_off(nav_window):
    nav_window.visit("http://pracuj.pl")

    nav_window.set_visual_mode(False)
    color_to_apply = "magenta"

    el1 = nav_window.find(
        (
            By.XPATH,
            "//div[@data-test='modal-cookie-bottom-bar']",
        ),
    )
    el2 = nav_window.find(
        (
            By.XPATH,
            "//div[@data-test='modal-cookie-bottom-bar']//descendant::button",
        ),
        highlight_color=color_to_apply,
    )
    el1_style = el1.get_attribute("style")
    el2_style = el2.get_attribute("style")
    time.sleep(1)
    assert (el1_style == "") and (color_to_apply in el2_style)
