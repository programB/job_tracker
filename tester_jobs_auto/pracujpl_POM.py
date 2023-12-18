import logging
import time
from typing import Tuple

from selenium.common import exceptions as SE
# from selenium.webdriver.chrome.webdriver import WebDriver
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

    Methods
    -------
    visit(url)
        causes the browsers to go to the url
    find(element, highlight=False)
        tries to find a given element on the webpage, may highlight it
    click(element)
        causes the browsers to click the webpage element
    enter_text(element, text)
        causes the browsers to enter the given text into the webpage element
    is_displayed(locator)
       checks whether an element indicated by locator is visible on the webpage
    """

    def __init__(self, driver) -> None:
        """
        Parameters
        ----------
        driver : WebDriver
            selenium webdriver object
        """
        # self.driver: WebDriver = driver
        self.driver = driver
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

    def find(self, element, highlight: bool = False) -> WebElement:
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
        element_found = self.driver.find_element(*element)
        if highlight:
            self._highlight(element_found)
        return element_found

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
        """Checks whether element indicated by locator is visible on the webpage

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
            logging.warning(f"Timeout of {self.timeout_sec}s reached while waiting for {locator}")
            return False

    def _highlight(self, element: WebElement):
        """Highlights an existing webpage element by changing its background

        After highlighting this method will trigger a 1 second pause

        Parameters
        ----------
        element : WebElement
            an existing element on the current webpage
        """
        self.driver.execute_script(
            "arguments[0].style.backgroundColor='red'",
            element,
        )
        time.sleep(1)
