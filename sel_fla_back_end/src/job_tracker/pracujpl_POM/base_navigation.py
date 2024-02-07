from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from selenium.common import exceptions as SE
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

if TYPE_CHECKING:
    from typing import List, Tuple

    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.remote.webelement import WebElement


class BaseNavigation:
    """Provides webpage basic operations"""

    _color_index = 0
    _colors = ["pink", "yellow", "lime", "lightblue", "lightgreen"]

    @classmethod
    def _get_color(cls) -> str:
        """Returns a html compatible color from a predefined list"""
        color = cls._colors[cls._color_index % len(cls._colors)]
        cls._color_index += 1
        return color

    def __init__(self, driver, visual_mode=False) -> None:
        """
        Parameters
        ----------
        driver : WebDriver
            selenium webdriver object
        visual_mode : bool
            global switch causing elements found using the find
            and find_all methods to get highlighted
        """
        self.driver: WebDriver = driver
        self._visual_mode = visual_mode
        self._timeout_sec = 5.0
        self._wait = WebDriverWait(self.driver, timeout=self._timeout_sec)

    @property
    def wait_with_timeout(self) -> WebDriverWait:
        """WebDriverWait object that uses the timeout_sec property to wait

        Example:
        element = driver_object.wait_with_timeout.
            until(expected_conditions.visibility_of_element_located(locator))

        Returns
        -------
        WebDriverWait
        """
        return self._wait

    @property
    def timeout_sec(self) -> float:
        """get/set timeout. Used by: wait_with_timeout, is_displayed()

        Parameters
        ----------
        timeout: float
            Number of seconds before timing out
        """
        return self._timeout_sec

    @timeout_sec.setter
    def timeout_sec(self, timeout: float):
        self._timeout_sec = timeout
        self._wait = WebDriverWait(self.driver, timeout=self._timeout_sec)

    def visit(self, url: str) -> None:
        """Causes the browsers to visit the url

        Parameters
        ----------
        url : str
            valid url of an existing webpage (eg. http://www.google.com)

        Raises
        ------
        ConnectionError if the browsers fails to navigate to the url
        """
        try:
            self.driver.get(url)
        except Exception as e:
            logging.warning("problem visiting the page at: %s", url)
            if "ERR_NAME_NOT_RESOLVED" in str(e):
                raise ConnectionError from e
            raise e

    def find(
        self,
        element,
        root_element: WebElement | None = None,
        highlight_color: str | None = None,
    ) -> WebElement:
        """Tries to find a given element in the current webpage

        Search from the page root or below a existing DOM object.
        Returns WebElement object on success or rises NoSuchElementException
        If element exists it can optionally be highlighted.


        Parameters
        ----------
        element : Tuple(str, str)
            element to look for. The first object of the tuple is the
            method to be used to look for it
            (use the selenium By enum eg.: By.TAG_NAME, BY.XPATH),
            second is the expression defining what to look for.
            example: (By.TAG_NAME, "div")
        root_element: WebElement | None, optional
            element below which to search. If not provided the search
            will be carried out from the document root.
        highlight_color : str | None , optional
            a html compatible color string  (eg. 'red') used to highlight
            the element (if found) for visual check by a human.
            (default is None - don't highlight BUT element highlighting may be
             forced globally by setting visual_mode True)

        Returns
        -------
        WebElement
            an object representing element found

        Raises
        ------
        NoSuchElementException
            If element couldn't be found
        """
        if root_element is None:
            element_found = self.driver.find_element(*element)
        else:
            element_found = root_element.find_element(*element)

        if self._visual_mode:
            self._highlight(element_found)
        elif highlight_color is not None:
            self._highlight(element_found, color=highlight_color)
        return element_found

    def find_all(
        self,
        element: Tuple[str, str],
        root_element: WebElement | None = None,
        highlight_color: str | None = None,
    ) -> List[WebElement]:
        """Tries to find all elements passed in the current webpage

        Search from the page root or below a existing DOM object.
        Returns WebElement objects list (empty if nothing is found)
        If elements exist they can optionally be highlighted

        Parameters
        ----------
        element : Tuple(str, str)
            element to look for. The first object of the tuple is the
            method to be used to look for it
            (use the selenium By enum eg.: By.TAG_NAME, BY.XPATH),
            second is the expression defining what to look for.
            example: (By.TAG_NAME, "div")
        root_element: WebElement | None, optional
            element below which to search. If not provided the search
            will be carried out from the document root.
        highlight_color : str | None , optional
            a html compatible color string  (eg. 'red') used to highlight
            the element (if found) for visual check by a human.
            (default is None - don't highlight BUT element highlighting may be
             forced globally by setting visual_mode True)

        Returns
        -------
        List[WebElement]
            list of objects representing elements found
            (empty if none found)
        """
        if root_element is None:
            elements_found = self.driver.find_elements(*element)
        else:
            elements_found = root_element.find_elements(*element)

        if self._visual_mode:
            for el_found in elements_found:
                self._highlight(el_found)
        elif highlight_color is not None:
            for el_found in elements_found:
                self._highlight(el_found, color=highlight_color)
        return elements_found

    def is_displayed(self, locator: Tuple[str, str]) -> bool:
        """Checks if element indicated by locator is visible on the webpage

        This method uses the wait_with_timeout object to allow a delay
        for an element to appear.
        It returns True if element is visible and False if element is not
        visible or doesn't exist at all in the DOM tree of the current webpage

        Parameters
        ----------
        locator : Tuple[str, str]
            element to look for.
            The first object of the tuple is the
            method to be used to look for it
            (use the selenium By enum eg.: By.TAG_NAME, BY.XPATH),
            second is the expression defining what to look for.
            example: (By.TAG_NAME, "div")

        Returns
        -------
        bool

        Raises
        ------
        TimeoutException
            If element dose not become visible within timeout period

        """
        try:
            self.wait_with_timeout.until(
                expected_conditions.visibility_of_element_located(locator),
            )
            return True
        except SE.TimeoutException:
            logging.warning("timeout: %s not visible", locator)
            return False

    def set_visual_mode(self, state: bool):
        """Highlight newly found elements

        If set to True elements found using find and find_all methods
        will get highlighted.
        If set to False elements will not get highlighted unless
        find or find_all methods are passed highlight_color to force
        highlight on a one off basis

        Parameters
        ----------
        state : bool
        """
        self._visual_mode = state

    def _highlight(self, element: WebElement, color="red"):
        """Highlights an existing webpage element by changing its background

        After highlighting this method will trigger a 1 second pause

        Parameters
        ----------
        element : WebElement
            an existing element on the current webpage
        color: str
            html valid color string. This is bypassed by an auto generated
            color if visual_mode is active
        """

        # When visual_mod is active use a color
        # from predefined sequence
        bgcolor = self._get_color() if self._visual_mode else color
        self.driver.execute_script(
            f"arguments[0].style.backgroundColor='{bgcolor}'",
            element,
        )
        time.sleep(1)
