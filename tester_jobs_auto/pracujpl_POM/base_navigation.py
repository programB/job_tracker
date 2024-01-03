import logging
import time
from typing import List, Tuple

from selenium.common import exceptions as SE
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


class BaseNavigation:
    """A class of basic operations on a webpage

    Attributes
    ----------
    driver : WebDriver
        selenium webdriver object
    timeout_sec: int
        a timeout setting used by the find method
    visual_mode: bool
        decides whether all newly found elements will get highlighted
        for human inspection

    Methods
    -------
    visit(url)
        causes the browsers to go to the url
    find(element, highlight=False)
        tries to find a given element on the webpage, may highlight it
    find_all(element, root_element, highlight_color=None)
        tries to find all elements, that match criteria, in the webpage
    click(element)
        causes the browsers to click the webpage element
    enter_text(element, text)
        causes the browsers to enter the given text into the webpage element
    is_displayed(locator)
       checks whether an element indicated by locator is visible on the webpage
    """

    _color_index: int = 0
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
        """
        # self.driver: WebDriver = driver
        self.driver = driver
        self._visual_mode = visual_mode
        self._timeout_sec = 5
        self._wait = WebDriverWait(self.driver, timeout=self._timeout_sec)

    @property
    def timeout_sec(self):
        """timeout getter"""
        return self._timeout_sec

    @timeout_sec.setter
    def timeout_sec(self, value):
        """timeout setter it modifies the _wait object when called

        Parameters
        ----------
        value : int
            new timeout value
        """
        self._timeout_sec = value
        self._wait = WebDriverWait(self.driver, timeout=self._timeout_sec)

    def visit(self, url: str) -> None:
        """Causes the browsers to visit the url given

        Raises ConnectionError if the browsers fails to navigate to the url

        Parameters
        ----------
        url : str
            valid url of an existing webpage (eg. http://www.google.com)
        """
        try:
            self.driver.get(url)
        except Exception as e:
            logging.warning(f"problem visiting the page at: {url}")
            if "ERR_NAME_NOT_RESOLVED" in str(e):
                raise ConnectionError
            else:
                raise e

    def find(
        self,
        element,
        root_element: WebElement | None = None,
        highlight_color: str | None = None,
    ) -> WebElement:
        """Tries to find a given element in the current webpage

        When element is found it returns a corresponding WebElement object
        If element can't be found it raises NoSuchElementException

        If element exists on the webpage it can optionally be highlighted
        using the _highlight method


        Parameters
        ----------
        element : Tuple(str, str)
            element to be looked for. The first object of the tuple is the
            method to be used to look for it as (as defined by the
            selenium By enum eg.: By.TAG_NAME, BY.XPATH),
            second is the expression defining what to look for.
            example: (By.TAG_NAME, "div")
        highlight : bool, optional
            decide if the element that could be found should be highlighted
            for visual check by a human (default is False - don't highlight)

        Returns
        -------
        WebElement
            an object representing element found
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
        element: tuple[str, str],
        root_element: WebElement | None = None,
        highlight_color: str | None = None,
    ) -> List[WebElement]:
        """Tries to find all elements, that match criteria, in the webpage

        When element(s) are found a list of corresponding WebElement objects
        is return if nothing can be found an empty list is returned.
        (this method as oposed to the .find method) WILL NOT rise exceptions.

        If elements exists on the webpage they can optionally be highlighted
        using the _highlight method


        Parameters
        ----------
        element : Tuple(str, str)
            element to be looked for. The first object of the tuple is the
            method to be used to look for it as (as defined by the
            selenium By enum eg.: By.TAG_NAME, BY.XPATH),
            second is the expression defining what to look for.
            example: (By.TAG_NAME, "div")
        root_element: WebElement | None
            an element relative to which the search should be carried out,
            if None the search will be performed from webpage's root
        highlight : bool, optional
            decide if the element that could be found should be highlighted
            for visual check by a human (default is False - don't highlight)

        Returns
        -------
        list[WebElement]
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

    def click(self, element: WebElement) -> None:
        """Causes the browsers to left click a webpage element

        Using this on an element that is not clickable has no effect.

        Parameters
        ----------
        element : WebElement
            a *existing* element on the current webpage (should be clickable)
        """
        element.click()

    def enter_text(self, element: WebElement, text: str) -> None:
        """Causes the browsers to enter the given text into the webpage element

        Raises ElementNotInteractableException error on attempt to enter
        a text into an element that does not support it (eg. not a text field)

        Parameters
        ----------
        element : WebElement
            an existing element on the current webpage that accepts text input
        text : str
            string to be entered into the element
        """
        element.send_keys(text)

    def is_displayed(self, locator: Tuple[str, str]) -> bool:
        """Checks if element indicated by locator is visible on the webpage

        This method uses the _wait object to allow a delay for an element
        to appear.
        It returns True if element is visible and False if element is not
        visible or doesn't exist at all in the DOM tree of the current webpage

        Parameters
        ----------
        locator : Tuple[str, str]
            element to be looked for. The first object of the tuple is the
            method to be used to look for it as (as defined by the
            selenium By enum eg.: By.TAG_NAME, BY.XPATH),
            second is the expression defining what to look for.
            example: (By.TAG_NAME, "div")
        Returns
        -------
        bool
        """
        try:
            self._wait.until(
                expected_conditions.visibility_of_element_located(locator),
            )
            return True
        except SE.TimeoutException:
            logging.warning(f"timeout: {locator} not visible")
            return False

    def set_visual_mode(self, state):
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
