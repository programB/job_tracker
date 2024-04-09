from __future__ import annotations

import re
from enum import Enum
from typing import TYPE_CHECKING

from flask import current_app
from selenium.common import exceptions as SE
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions

from .base_navigation import AdsPopup, BaseNavigation

if TYPE_CHECKING:
    from typing import Tuple

    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.remote.webelement import WebElement


class Distance(Enum):
    """Represents finite choice of search radii (around desired location)"""

    ZERO_KM = 0
    TEN_KM = 10
    TWENTY_KM = 20
    THIRTY_KM = 30
    FIFTY_KM = 50
    HUNDRED_KM = 100


class OptionsMenu(BaseNavigation):
    """Represents any folding menu with multiple choices"""

    def __init__(
        self,
        driver: WebDriver,
        main_locator: Tuple[str, str],
        btn_rel_locator: str,
        option_rel_locators: dict,
        visual_mode=False,
    ) -> None:
        """

        Parameters
        ----------
        driver : WebDriver
            selenium webdriver object
        visual_mode : bool
            global switch causing elements found using the find
            and find_all methods to get highlighted
        main_locator : Tuple[str, str]
            locator pointing to a top level grouping element
            The first object of the tuple is the
            method to be used to look for it
            (use the selenium By enum eg.: By.TAG_NAME, BY.XPATH),
            second is the expression defining what to look for.
            example: (By.TAG_NAME, "div")
        btn_rel_locator : str
            locator string used to find the top level clickable element
            that revels options (when clicked)
            (it must use the same searching BY method as the main_locator)
        option_rel_locators : dict
            dict of locator strings pointing to individual options
            (they must use the same searching BY method as the main_locator)
        """
        self.driver = driver
        self._main_locator = main_locator
        self._btn_rel_locator = btn_rel_locator
        self._option_locators = option_rel_locators
        super().__init__(driver, visual_mode)

    @property
    def menu(self) -> WebElement:
        self.timeout_sec = max(self.timeout_sec, 3.0)

        # x will be set to self.driver
        menu: WebElement = self.wait_with_timeout.until(
            lambda x: x.find_element(
                self._main_locator[0],
                self._main_locator[1] + self._btn_rel_locator,
            )
        )
        return menu

    def select(self, options: list[str]) -> None:
        """Select options from the menu using the _option_locators dictionary

        Unknown options are skipped (warning is logged)

        Parameters
        ----------
        options : list[str]
            a list desired keys from the _option_locators dictionary
        """
        for option in options:
            if option in self._option_locators.keys():
                try:
                    # unfold menu
                    self.menu.click()
                    element = self.wait_with_timeout.until(
                        expected_conditions.visibility_of_element_located(
                            (
                                self._main_locator[0],
                                self._main_locator[1]
                                + self._option_locators[
                                    option
                                ],  # noqa: E501 pylint: disable=locally-disabled, line-too-long
                            )
                        )
                    )
                    if "selected" not in element.get_attribute("class"):
                        self._scroll_into_view(element)
                        element.click()
                except SE.NoSuchElementException:
                    current_app.logger.warning("%s not found in the menu", option)
                finally:
                    # fold menu
                    self.menu.click()
            else:
                current_app.logger.warning(
                    "unable to select unknown option: %s", option
                )

    def is_selected(self, option: str) -> bool:
        """Check the webpage if given option is indeed selected

        Parameters
        ----------
        option : str
            A valid key from the _option_locators dictionary

        Returns
        -------
        bool
        """
        if option in self._option_locators.keys():
            try:
                # unfold menu
                self.menu.click()
                element = self.wait_with_timeout.until(
                    expected_conditions.visibility_of_element_located(
                        (
                            self._main_locator[0],
                            self._main_locator[1]
                            + self._option_locators[
                                option
                            ],  # noqa: E501 pylint: disable=locally-disabled, line-too-long
                        )
                    )
                )
                # FIRST check selection condition THEN close menu.
                # Shortening this to self.menu.click(); return "selected" in...
                # leads to StaleElementReferenceException
                is_sel = (
                    False
                    if element.get_attribute("class") is None
                    else "selected" in element.get_attribute("class")
                )
                self.menu.click()
                return is_sel
            except SE.NoSuchElementException:
                current_app.logger.warning("%s not found in the menu", option)
                return False
        return False

    def _scroll_into_view(self, element: WebElement) -> None:
        script = "arguments[0].scrollIntoView();"
        self.driver.execute_script(script, element)


class CookieChoice(BaseNavigation):
    """Represents cookie consent overlay"""

    @property
    def _overlay_cookie_consent(self) -> WebElement | None:
        """Looks for cookie consent overlay top level element

        Returns
        -------
        WebElement | None
            WebElement if element was found None otherwise (logs failure)
        """
        cookie_overlay = None
        try:
            cookie_overlay = self.wait_with_timeout.until(
                expected_conditions.visibility_of_element_located(
                    (
                        By.XPATH,
                        "//div[@data-test='modal-cookie-bottom-bar']",
                    ),
                )
            )

        except (SE.NoSuchElementException, SE.TimeoutException):
            current_app.logger.warning("Cookie consent modal was not found.")
        return cookie_overlay

    def _is_visible(self) -> bool:
        """Check cookie consent overlay visibility

        Returns
        -------
        bool
        """
        cookie_overlay = self._overlay_cookie_consent
        return (cookie_overlay is not None) and cookie_overlay.is_displayed()

    def reject_non_essential_cookies(self):
        """Chooses to reject non essential cookies and dismisses the overlay"""
        if self._is_visible():
            btn_customize_cookies = self.find(
                (
                    By.XPATH,
                    "//div[contains(@class, 'cookies')]//descendant::button[@data-test='button-customizeCookie']",  # noqa: E501 pylint: disable=locally-disabled, line-too-long
                ),
            )
            btn_customize_cookies.click()
            btn_save_cookie_settings = self.find(
                (
                    By.XPATH,
                    "//div[@data-test='modal-cookie-customize']//descendant::button[@data-test='button-submit']",  # noqa: E501 pylint: disable=locally-disabled, line-too-long
                ),
            )
            btn_save_cookie_settings.click()

    def accept_all_cookies(self):
        """Chooses to accept all cookies and dismisses the overlay"""
        if self._is_visible():
            btn_accept_all_cookies = self.find(
                (
                    By.XPATH,
                    "//div[contains(@class, 'cookies')]//descendant::button[@data-test='button-submitCookie']",  # noqa: E501 pylint: disable=locally-disabled, line-too-long
                ),
            )
            btn_accept_all_cookies.click()


class PracujplMainPage(BaseNavigation):
    """Models pracuj.pl home page"""

    def __init__(
        self,
        driver,
        url=None,
        reject_cookies=False,
        visual_mode=False,
        attempt_closing_popups=True,
        timeout=5.0,
    ) -> None:
        """

        Parameters
        ----------
        driver : WebDriver
            selenium webdriver object
        url: custom url for the pracuj.pl website.
            If not given it will be set to https://www.pracuj.pl
        visual_mode: bool
            decides whether all newly found elements will get highlighted
            for human inspection
        reject_cookies : bool
            when True: causes non-essential cookies to be rejected
            on visiting the homepage
            when False: causes all cookies to be accepted
        timeout: float
            sets timeout for find operations
        """
        super().__init__(driver, visual_mode, timeout)
        if url is None:
            self.visit("https://www.pracuj.pl")
        else:
            try:
                self.visit(url)
            except Exception as e:
                current_app.logger.fatal(
                    "Error connecting to pracuj.pl website at %s", url
                )
                raise e
        if attempt_closing_popups:
            AdsPopup(driver, visual_mode, timeout).close()
        if reject_cookies:
            CookieChoice(driver, visual_mode, timeout).reject_non_essential_cookies()
        else:
            CookieChoice(driver, visual_mode, timeout).accept_all_cookies()
        self._search_bar_box = [
            None,
            (
                By.XPATH,
                "//div[@data-test='section-search-bar' or @data-test='section-search-bar-it']",  # noqa: E501 pylint: disable=locally-disabled, line-too-long
            ),
        ]

        self._btn_search_submit = [
            None,
            (
                By.XPATH,
                ".//descendant::div[@data-test='section-search-with-filters' or @data-test='section-search-with-filters-it']/button",  # noqa: E501 pylint: disable=locally-disabled, line-too-long
            ),
        ]
        self.job_level = OptionsMenu(
            self.driver,
            main_locator=(By.XPATH, "//div[@data-test='dropdown-element-et']"),
            btn_rel_locator="//descendant::button[1]",
            option_rel_locators={
                "trainee": "//descendant::div[@data-test='select-option-1']",
                "assistant": "//descendant::div[@data-test='select-option-3']",
                "junior": "//descendant::div[@data-test='select-option-17']",
                "mid_regular": "//descendant::div[@data-test='select-option-4']",  # noqa: E501 pylint: disable=locally-disabled, line-too-long
                "senior": "//descendant::div[@data-test='select-option-18']",
                "expert": "//descendant::div[@data-test='select-option-19']",
                "manager": "//descendant::div[@data-test='select-option-5']",
                "director": "//descendant::div[@data-test='select-option-6']",
                "president": "//descendant::div[@data-test='select-option-21']",  # noqa: E501 pylint: disable=locally-disabled, line-too-long
                "laborer": "//descendant::div[@data-test='select-option-21']",
            },
        )
        self.contract_type = OptionsMenu(
            self.driver,
            main_locator=(By.XPATH, "//div[@data-test='dropdown-element-tc']"),
            btn_rel_locator="//descendant::button[1]",
            option_rel_locators={
                "o_prace": "//descendant::div[@data-test='select-option-0']",
                "o_dzielo": "//descendant::div[@data-test='select-option-1']",
                "zlecenie": "//descendant::div[@data-test='select-option-2']",
                "B2B": "//descendant::div[@data-test='select-option-3']",
                "o_zastepstwo": "//descendant::div[@data-test='select-option-4']",  # noqa: E501 pylint: disable=locally-disabled, line-too-long
                "agencyjna": "//descendant::div[@data-test='select-option-5']",
                "o_prace_tymczasowa": "//descendant::div[@data-test='select-option-6']",  # noqa: E501 pylint: disable=locally-disabled, line-too-long
                "praktyki": "//descendant::div[@data-test='select-option-7']",
            },
        )
        self.employment_type_menu = OptionsMenu(
            self.driver,
            main_locator=(By.XPATH, "//div[@data-test='dropdown-element-ws']"),
            btn_rel_locator="//descendant::button[1]",
            option_rel_locators={
                "part_time": "//descendant::div[@data-test='select-option-1']",
                "temporary": "//descendant::div[@data-test='select-option-2']",
                "full_time": "//descendant::div[@data-test='select-option-0']",
            },
        )
        self.job_mode = OptionsMenu(
            self.driver,
            main_locator=(By.XPATH, "//div[@data-test='dropdown-element-wm']"),
            btn_rel_locator="//descendant::button[1]",
            option_rel_locators={
                "full_office": "//descendant::div[@data-test='select-option-full-office']",  # noqa: E501 pylint: disable=locally-disabled, line-too-long
                "hybrid": "//descendant::div[@data-test='select-option-hybrid']",  # noqa: E501 pylint: disable=locally-disabled, line-too-long
                "home_office": "//descendant::div[@data-test='select-option-home-office']",  # noqa: E501 pylint: disable=locally-disabled, line-too-long
                "mobile": "//descendant::div[@data-test='select-option-mobile']",  # noqa: E501 pylint: disable=locally-disabled, line-too-long
            },
        )
        self._search_field = [
            None,
            (
                By.XPATH,
                ".//descendant::label[contains(text(), 'Stanowisko, firma, słowo kluczowe') or contains(text(), 'Посада, компанія, ключове слово')]/preceding-sibling::input[@data-test='input-field']",  # noqa: E501 pylint: disable=locally-disabled, line-too-long
            ),
        ]
        self._category_field = [
            None,
            (
                By.XPATH,
                ".//descendant::label[contains(text(), 'Kategoria') or contains(text(), 'Категорія')]/preceding-sibling::input[@data-test='input-field']",  # noqa: E501 pylint: disable=locally-disabled, line-too-long
            ),
        ]
        self._location_field = [
            None,
            (
                By.XPATH,
                ".//descendant::label[contains(text(), 'Lokalizacja') or contains(text(), 'Розташування')]/preceding-sibling::input[@data-test='input-field']",  # noqa: E501 pylint: disable=locally-disabled, line-too-long
            ),
        ]

    @property
    def _search_mode_selector(self):
        try:
            return self.wait_with_timeout.until(
                expected_conditions.visibility_of_element_located(
                    (
                        By.XPATH,
                        "//div[@data-test='section-subservices']",
                    )
                )
            )
        except SE.NoSuchElementException as e:
            current_app.logger.error("couldn't find search mode selector")
            raise e

    @property
    def search_mode(self) -> str:
        """The broad domain of job offers to search in

        Currently supported are:
        'default' - all job offers are considered before specific filters
        are applied
        'it' - restricts the search to IT sector job offers (other filter
        can still be applied)

        Returns
        -------
        mode : str
            currently set mode, empty string means unsupported mode
        """
        selector = self.find(
            (By.XPATH, ".//descendant::span[contains(@class, 'selected')]"),
            root_element=self._search_mode_selector,
        )
        match selector.get_attribute("data-test"):
            case "tab-item-default":
                return "default"
            case "tab-item-it":
                return "it"
            case _:
                return ""

    @search_mode.setter
    def search_mode(self, mode: str):
        match mode:
            case "default":
                xpath = ".//descendant::span[@data-test='tab-item-default']"
            case "it":
                xpath = ".//descendant::span[@data-test='tab-item-it']"
            case _:
                current_app.logger.error(
                    "unknown search mode %s, valid: 'default', 'it'",
                    mode,
                )
                return
        selector = self.find(
            (By.XPATH, xpath),
            root_element=self._search_mode_selector,
        )
        selector.click()

    @property
    def search_term(self) -> str:
        """Key word to search for

        Returns
        -------
        str
        """
        value = self.search_field.get_attribute("value")
        return "" if value is None else value

    @search_term.setter
    def search_term(self, value: str):
        self.search_field.send_keys(value)
        # Sending the enter key started to cause
        # the search to begin immediately.
        # self.search_field.send_keys(Keys.ENTER)

    @property
    def _location(self) -> str:
        value = self.location_field.get_attribute("value")
        return "" if value is None else value

    @_location.setter
    def _location(self, value: str):
        self.location_field.send_keys(value)
        self.location_field.send_keys(Keys.ENTER)

    @property
    def _distance_dropdown(self) -> WebElement:
        self.driver.maximize_window()
        try:
            dist_dropdown = self.find(
                (
                    By.XPATH,
                    "//div[@data-test='dropdown-element-rd']",
                )
            )
        except SE.NoSuchElementException as e:
            current_app.logger.error("couldn't find distance dropdown")
            raise e
        return dist_dropdown

    @property
    def _distance(self) -> Distance:
        try:
            d_filed = self.find(
                (
                    By.XPATH,
                    ".//descendant::input[@data-test='input-field' and @value]",  # noqa: E501 pylint: disable=locally-disabled, line-too-long
                ),
                root_element=self._distance_dropdown,
            )
            str_d_value = d_filed.get_attribute("value")
        except SE.NoSuchElementException as e:
            current_app.logger.error("couldn't find distance dropdown")
            raise e
        # example str_d_value looks like this: "+30 km"
        m = re.match(r"^\+(?P<dist>[0-9]*)\skm$", str_d_value)
        for dist in list(Distance):
            if int(m["dist"]) == dist.value:
                return dist
        return Distance.ZERO_KM

    @_distance.setter
    def _distance(self, distance: Distance):
        option_rel_locators = {
            Distance.ZERO_KM: ".//li[@data-test='select-option-0']",
            Distance.TEN_KM: ".//li[@data-test='select-option-10']",
            Distance.TWENTY_KM: ".//li[@data-test='select-option-20']",
            Distance.THIRTY_KM: ".//li[@data-test='select-option-30']",
            Distance.FIFTY_KM: ".//li[@data-test='select-option-50']",
            Distance.HUNDRED_KM: ".//li[@data-test='select-option-100']",
        }
        self._distance_dropdown.click()
        self.find(
            (By.XPATH, option_rel_locators.get(distance)),
            root_element=self._distance_dropdown,
        ).click()

    @property
    def location_and_distance(self) -> tuple[str, Distance]:
        """Location (and radius around it) in which to search for offers

        Returns
        -------
        tuple[str, Distance]
          name of the city, radius around that location
        """
        return (self._location, self._distance)

    @location_and_distance.setter
    def location_and_distance(self, value: tuple[str, Distance]):
        self._location = value[0]
        self._distance = value[1]

    @property
    def employment_type(self) -> list[str]:
        """Employment type (can be multiple) from a predefined list

        'part_time', 'temporary', 'full_time'

        Returns
        -------
        list[str]
        """
        selected = []
        for emp_type in self.employment_type_menu._option_locators.keys():
            if self.employment_type_menu.is_selected(emp_type):
                selected.append(emp_type)
        return selected

    @employment_type.setter
    def employment_type(self, choices: list[str]):
        self.driver.maximize_window()
        self.employment_type_menu.select(choices)

    @property
    def search_bar_box(self) -> WebElement:
        try:
            self._search_bar_box[0] = self.find(
                self._search_bar_box[1],
            )
        except SE.NoSuchElementException as e:
            current_app.logger.critical("search box was not found")
            raise e
        return self._search_bar_box[0]

    def start_searching(self):
        """Begin the search with currently set criteria"""
        btn_search_submit = self._get_search_bar_control(
            self._btn_search_submit,
        )
        btn_search_submit.click()

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

    def _get_search_bar_control(self, control):
        try:
            current_app.logger.warning("Looking for %s", control)
            control[0] = self.find(
                control[1],
                root_element=self.search_bar_box,
            )
        except SE.NoSuchElementException as e:
            current_app.logger.critical("%s was not found", control[0])
            raise e
        return control[0]
