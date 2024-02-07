import unittest.mock
from typing import List

import pytest
from selenium.common import exceptions as SE
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from job_tracker.pracujpl_POM import BaseNavigation


@pytest.fixture
def mock_driver():
    driver: WebDriver = unittest.mock.create_autospec(WebDriver)
    return driver


@pytest.mark.skip
def test_mock_driver_fixture(mock_driver):
    assert isinstance(mock_driver, WebDriver)


@pytest.fixture
def mock_element():
    element = unittest.mock.create_autospec(WebElement)
    return element


@pytest.mark.skip
def test_mock_element_fixture(mock_element):
    assert isinstance(mock_element, WebElement)


def test_should_create_BaseNavigation(mock_driver):
    assert BaseNavigation(mock_driver) is not None


@pytest.mark.parametrize(
    "prop",
    [
        "timeout_sec",
    ],
)
def test_should_enssure_properties_existence(prop):
    assert hasattr(BaseNavigation, prop)


@pytest.mark.parametrize(
    "method",
    [
        "visit",
        "find",
        "find_all",
        "is_displayed",
    ],
)
def test_should_enssure_methods_existence(method):
    assert hasattr(BaseNavigation, method)
    # Can't do:
    # assert callable(BaseNavigation.visit)
    # directly because method is a str.
    # Doing __dict__[method] istead
    assert callable(BaseNavigation.__dict__[method])


class TestVisit:
    """Unit tests for: BaseNavigation.visit"""

    def test_successful_visit_existing_url(self, mock_driver):
        # GIVEN a valid url
        existing_url = "https://www.valid_fake.url.com"
        #  AND mock_driver.get will return None
        mock_driver.get.return_value = None
        #  AND mock_driver.title will return set title
        fake_title = "Title of a fake page"
        mock_driver.title = fake_title
        #  AND browser_window is created
        browser_window = BaseNavigation(mock_driver)
        # WHEN opening url
        browser_window.visit(existing_url)
        # THEN page title should be "Title of a fake page"
        assert fake_title.casefold() in browser_window.driver.title.casefold()
        #  AND
        mock_driver.get.assert_called_once_with(existing_url)

    def test_failure_visit_not_existing_url(self, mock_driver):
        # GIVEN not existing url
        not_existing_url = "https://www.invalid_fake.url.com"
        # AND calling mock_driver.get will rise ConnectionError
        mock_driver.get.side_effect = ConnectionError
        # WHEN opening not existing website
        # THEN BaseNavigation.visit should rise ConnectionError
        with pytest.raises(ConnectionError):
            browser_window = BaseNavigation(mock_driver)
            browser_window.visit(not_existing_url)
        # AND
        mock_driver.get.assert_called_once_with(not_existing_url)

    @pytest.mark.parametrize("invalid_type_as_url", [3, ("smth", 4)])
    def test_passing_invalid_type_as_url(self, mock_driver, invalid_type_as_url):
        mock_driver.get.side_effect = SE.InvalidArgumentException
        with pytest.raises(SE.InvalidArgumentException):
            browser_window = BaseNavigation(mock_driver)
            browser_window.visit(invalid_type_as_url)


class TestFind:
    """Unit tests for: BaseNavigation.find"""

    @pytest.mark.parametrize("highlight_clr", [None, "red", "blue"])
    @pytest.mark.parametrize(
        "tag_to_find",
        [
            (By.TAG_NAME, "body"),
            (By.XPATH, "body"),
        ],
    )
    def test_successful_find_starting_from_page_root(
        self, mock_driver, mock_element, highlight_clr, tag_to_find
    ):
        # GIVEN mock_driver.find_element will return WebElement
        # assert isinstance(mock_element, WebElement)
        mock_driver.find_element.return_value = mock_element
        #  AND browser_window is created
        browser_window = BaseNavigation(mock_driver)
        # WHEN trying to find an element
        found_object = browser_window.find(
            tag_to_find,
            root_element=None,
            highlight_color=highlight_clr,
        )
        # THEN what is found is a WebElement
        # AND it is such regardless whether highlighting was requested
        assert isinstance(found_object, WebElement)

    # @pytest.mark.parametrize("parent_element", ["mock_element", "non"])
    # @pytest.mark.parametrize("parent_element", [None])
    # def test_should_find_a_tag_with_given_parent_tag(
    @pytest.mark.parametrize("highlight_clr", [None, "red", "blue"])
    def test_successful_find_starting_from_other_tag(
        self, mock_driver, mock_element, highlight_clr
    ):
        # mock_parent_element = request.getfixturevalue(parent_element)
        # GIVEN WebElement find_element method will return WebElement obj
        mock_parent_element = mock_element
        mock_parent_element.find_element.return_value = mock_element
        # AND BaseNavigation obj is created
        browser_window = BaseNavigation(mock_driver)
        # WHEN looking for some tag - descendant of other exisintg WebElement
        tag_to_find = (By.TAG_NAME, "body")
        found_object = browser_window.find(
            tag_to_find,
            root_element=mock_parent_element,
            highlight_color=highlight_clr,
        )
        # THEN found object should be WebElement type obj
        #      regardless whether highlighting was requested
        assert isinstance(found_object, WebElement)

    @pytest.mark.parametrize("highlight_clr", [None, "red", "blue"])
    def test_failure_to_find_starting_from_page_root(
        self, mock_driver, mock_element, highlight_clr
    ):
        # GIVEN mock_driver.find_element will rise NoSuchElementException
        mock_driver.find_element.side_effect = SE.NoSuchElementException
        #  AND browser_window is created
        browser_window = BaseNavigation(mock_driver)
        # WHEN trying to find an element
        not_existing_tag = (By.TAG_NAME, "nosuchtag")
        # THEN BaseNavigation.find should rise NoSuchElementException
        with pytest.raises(SE.NoSuchElementException):
            browser_window.find(
                not_existing_tag,
                root_element=None,
                highlight_color=highlight_clr,
            )

    @pytest.mark.parametrize("highlight_clr", [None, "red", "blue"])
    def test_failure_to_find_starting_from_other_tag(
        self, mock_driver, mock_element, highlight_clr
    ):
        # GIVEN mock_element.find_element will rise NoSuchElementException
        mock_parent_element = mock_element
        mock_parent_element.find_element.side_effect = SE.NoSuchElementException
        #  AND browser_window is created
        browser_window = BaseNavigation(mock_driver)
        # WHEN trying to find an element
        not_existing_tag = (By.TAG_NAME, "nosuchtag")
        # THEN BaseNavigation.find should rise NoSuchElementException
        with pytest.raises(SE.NoSuchElementException):
            browser_window.find(
                not_existing_tag,
                root_element=mock_parent_element,
                highlight_color=highlight_clr,
            )

    @pytest.mark.parametrize(
        "wrong_locator",
        [
            None,
            "single string",
            ("string1", "string2"),
        ],
    )
    def test_bad_type_for_element_argument(self, mock_driver, wrong_locator):
        browser_window = BaseNavigation(mock_driver)
        mock_driver.find_element.side_effect = SE.InvalidArgumentException
        with pytest.raises((TypeError, SE.InvalidArgumentException)):
            browser_window.find(
                wrong_locator,
                root_element=None,
                highlight_color=None,
            )

    @pytest.mark.parametrize(
        "invalid_root_object",
        [
            "single string",
            ("string1", "string2"),
            "",
            object,
            3,
        ],
    )
    def test_bad_type_for_parent_element_argument(
        self, mock_driver, invalid_root_object
    ):
        tag_to_find = (By.TAG_NAME, "body")
        browser_window = BaseNavigation(mock_driver)
        with pytest.raises(AttributeError):
            browser_window.find(
                tag_to_find,
                root_element=invalid_root_object,
                highlight_color=None,
            )


class TestFindAll:
    """Unit tests for: BaseNavigation.find_all"""

    @pytest.mark.parametrize("highlight_clr", [None, "red", "blue"])
    @pytest.mark.parametrize(
        "tag_to_find",
        [
            (By.TAG_NAME, "body"),
            (By.XPATH, "body"),
        ],
    )
    def test_successful_find_starting_from_page_root(
        self, mock_driver, mock_element, highlight_clr, tag_to_find
    ):
        # GIVEN mock_driver.find_elements will return List[WebElement]
        mock_driver.find_elements.return_value = [mock_element]
        #  AND browser_window is created
        browser_window = BaseNavigation(mock_driver)
        # WHEN trying to find an element
        found_object = browser_window.find_all(
            tag_to_find,
            root_element=None,
            highlight_color=highlight_clr,
        )
        # THEN what is found is List[WebElement]
        # AND it is such regardless whether highlighting was requested
        assert isinstance(found_object, List)
        for item in found_object:
            assert isinstance(item, WebElement)

    # @pytest.mark.parametrize("parent_element", ["mock_element", "non"])
    # @pytest.mark.parametrize("parent_element", [None])
    # def test_should_find_a_tag_with_given_parent_tag(
    @pytest.mark.parametrize("highlight_clr", [None, "red", "blue"])
    def test_successful_find_starting_from_other_tag(
        self, mock_driver, mock_element, highlight_clr
    ):
        # mock_parent_element = request.getfixturevalue(parent_element)
        # GIVEN WebElement find_element method will return WebElement obj
        mock_parent_element = mock_element
        mock_parent_element.find_elements.return_value = [mock_element]
        # AND BaseNavigation obj is created
        browser_window = BaseNavigation(mock_driver)
        # WHEN looking for some tag - descendant of other exisintg WebElement
        tag_to_find = (By.TAG_NAME, "body")
        found_object = browser_window.find_all(
            tag_to_find,
            root_element=mock_parent_element,
            highlight_color=highlight_clr,
        )
        # THEN found object should be WebElement type obj
        #      regardless whether highlighting was requested
        assert isinstance(found_object, List)
        for item in found_object:
            assert isinstance(item, WebElement)

    @pytest.mark.parametrize("highlight_clr", [None, "red", "blue"])
    def test_failure_to_find_starting_from_page_root(self, mock_driver, highlight_clr):
        # GIVEN mock_driver.find_elements will return empty list
        mock_driver.find_elements.return_value = []
        # GIVEN browser_window is created
        browser_window = BaseNavigation(mock_driver)
        # WHEN trying to find not existing elements
        not_existing_tag = (By.TAG_NAME, "nosuchtag")
        found_object = browser_window.find_all(
            not_existing_tag,
            root_element=None,
            highlight_color=highlight_clr,
        )
        # THEN BaseNavigation.find should return empty list
        assert found_object == []

    @pytest.mark.parametrize("highlight_clr", [None, "red", "blue"])
    def test_failure_to_find_starting_from_other_tag(
        self, mock_driver, mock_element, highlight_clr
    ):
        # GIVEN mock_element.find_element will rise NoSuchElementException
        mock_parent_element = mock_element
        mock_parent_element.find_elements.return_value = []
        #  AND browser_window is created
        browser_window = BaseNavigation(mock_driver)
        # WHEN trying to find an element
        not_existing_tag = (By.TAG_NAME, "nosuchtag")
        # THEN BaseNavigation.find should rise NoSuchElementException
        found_object = browser_window.find_all(
            not_existing_tag,
            root_element=mock_parent_element,
            highlight_color=highlight_clr,
        )
        # THEN BaseNavigation.find should return empty list
        assert found_object == []

    @pytest.mark.parametrize(
        "wrong_locator",
        [
            None,
            "single string",
            ("string1", "string2"),
        ],
    )
    def test_bad_type_for_element_argument(self, mock_driver, wrong_locator):
        browser_window = BaseNavigation(mock_driver)
        mock_driver.find_elements.side_effect = SE.InvalidArgumentException
        with pytest.raises((TypeError, SE.InvalidArgumentException)):
            browser_window.find_all(
                wrong_locator,
                root_element=None,
                highlight_color=None,
            )

    @pytest.mark.parametrize(
        "invalid_root_object",
        [
            "single string",
            ("string1", "string2"),
            "",
            object,
            3,
        ],
    )
    def test_bad_type_for_parent_element_argument(
        self, mock_driver, invalid_root_object
    ):
        tag_to_find = (By.TAG_NAME, "body")
        browser_window = BaseNavigation(mock_driver)
        with pytest.raises(AttributeError):
            browser_window.find(
                tag_to_find,
                root_element=invalid_root_object,
                highlight_color=None,
            )
