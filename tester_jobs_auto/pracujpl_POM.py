import logging
import time
from typing import Tuple

from selenium.common import exceptions as SE
from selenium.webdriver.common.by import By
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
    visual_mode: bool
        decides whether all newly found elements will get highlighted
        for human inspection

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

    _color_index: int = 0
    _highlight_colors = ["pink", "yellow", "lime", "lightblue", "lightgreen"]

    @classmethod
    def _get_color(cls) -> str:
        """Returns a html compatible color from a predefined list"""
        color = cls._highlight_colors[cls._color_index % len(cls._highlight_colors)]
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

    def find(self, element, highlight_color: str | None = None) -> WebElement:
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
        if self._visual_mode:
            self._highlight(element_found)
        elif highlight_color is not None:
            self._highlight(element_found, color=highlight_color)
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


class PracujplMainPage(BaseNavigation):
    def __init__(self, driver, visual_mode=False, reject_cookies=False) -> None:
        super().__init__(driver, visual_mode)
        self._overlay_cookie_consent = [
            None,
            (
                By.XPATH,
                "//div[@data-test='modal-cookie-bottom-bar']",
            ),
        ]
        self._search_bar_box = [
            None,
            (By.XPATH, "//div[@data-test='section-search-bar']"),
        ]

        # Working code
        self._btn_search_submit = [
            None,
            (
                By.XPATH,
                ".//descendant::div[@data-test='section-search-with-filters']/button",
                # ".//descendant::button[6]",  # works
                # ".//descendant::button[last()]",  # doesn't work. selects [1]
                # ".//descendant::button::[last()]",  # :( invalid xpath expression
                # ".//descendant::button:last-child",  # :( unresolvable namespaces
                # ".//descendant::button:last-of-type",  # :( unresolvable namespaces
            ),
        ]
        self._search_field = [
            None,
            (
                By.XPATH,
                ".//descendant::div[@data-test='section-search-bar-parameters']//descendant::input[@data-test='input-field'][1]",
            ),
        ]
        self._category_field = [
            None,
            (
                By.XPATH,
                ".//descendant::div[@data-test='section-search-bar-parameters']//descendant::input[@data-test='input-field'][2]",
            ),
        ]
        self._location_field = [
            None,
            (
                By.XPATH,
                ".//descendant::div[@data-test='section-search-bar-parameters']//descendant::input[@data-test='input-field'][3]",
            ),
        ]
        self._distance_field = [
            None,
            (
                By.XPATH,
                ".//descendant::div[@data-test='section-search-bar-parameters']//descendant::input[@data-test='input-field'][4]",
            ),
        ]

        self.visit("https://www.pracuj.pl")
        if reject_cookies:
            self._reject_non_essential_cookies()
        else:
            self._accept_all_cookies()

    @property
    def overlay_cookie_consent(self):
        if self._overlay_cookie_consent[0] is None:
            try:
                self._overlay_cookie_consent[0] = self.find(
                    self._overlay_cookie_consent[1],
                )
            except SE.NoSuchElementException as e:
                logging.info("cookie consent modal was not found")
        return self._overlay_cookie_consent[0]

    @property
    def search_bar_box(self) -> WebElement:
        if self._search_bar_box[0] is None:
            try:
                self._search_bar_box[0] = self.find(
                    self._search_bar_box[1],
                )
            except SE.NoSuchElementException as e:
                logging.critical("search box was not found")
                raise e
        return self._search_bar_box[0]

    @property
    def btn_search_submit(self) -> WebElement:
        return self._get_search_bar_control(
            self._btn_search_submit,
        )

    @property
    def search_field(self) -> WebElement:
        return self._get_search_bar_control(
            self._search_field,
        )

    @property
    def category_field(self) -> WebElement:
        return self._get_search_bar_control(
            self._category_field,
        )

    @property
    def location_field(self) -> WebElement:
        return self._get_search_bar_control(
            self._location_field,
        )

    @property
    def distance_field(self) -> WebElement:
        return self._get_search_bar_control(
            self._distance_field,
        )

    def _get_search_bar_control(self, control):
        if control[0] is None:
            try:
                control[0] = self.search_bar_box.find_element(*control[1])
            except SE.NoSuchElementException as e:
                logging.critical(f"{control[0]} was not found")
                raise e
        return control[0]

    def _reject_non_essential_cookies(self):
        # if self.find(self.overlay_cookie_consent, highlight=self._visual_mode):
        if self.overlay_cookie_consent is not None:
            btn_customize_cookies = self.find(
                (
                    By.XPATH,
                    "//div[contains(@class, 'cookies')]//descendant::button[@data-test='button-customizeCookie']",
                ),
            )
            btn_customize_cookies.click()
            btn_save_cookie_settings = self.find(
                (
                    By.XPATH,
                    "//div[@data-test='modal-cookie-customize']//descendant::button[@data-test='button-submit']",
                ),
            )
            btn_save_cookie_settings.click()

    def _accept_all_cookies(self):
        if self.overlay_cookie_consent is not None:
            btn_accept_all_cookies = self.find(
                (
                    By.XPATH,
                    "//div[contains(@class, 'cookies')]//descendant::button[@data-test='button-submitCookie']",
                ),
            )
            btn_accept_all_cookies.click()
