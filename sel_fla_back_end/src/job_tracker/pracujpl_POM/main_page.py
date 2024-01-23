import logging
import re
from enum import Enum
from typing import Tuple

from selenium.common import exceptions as SE
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions

from .base_navigation import BaseNavigation


class Distance(Enum):
    """Enum represents finite choice of search radii (around desired location)"""

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
        # driver: WebDriver,
        driver,
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
        if self.timeout_sec < 3.0:
            self.timeout_sec = 3.0

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
                                self._main_locator[1] + self._option_locators[option],
                            )
                        )
                    )
                    if "selected" not in element.get_attribute("class"):
                        self._scroll_into_view(element)
                        element.click()
                except SE.NoSuchElementException:
                    logging.warning(f"{option} not found in the menu")
                finally:
                    # fold menu
                    self.menu.click()
            else:
                logging.warning(f"unable to select unknown option: {option}")

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
                            self._main_locator[1] + self._option_locators[option],
                        )
                    )
                )
                if "selected" in element.get_attribute("class"):
                    # fold menu
                    self.menu.click()
                    return True
                else:
                    # fold menu
                    self.menu.click()
                    return False
            except SE.NoSuchElementException:
                logging.warning(f"{option} not found in the menu")
                return False
        return False

    def _scroll_into_view(self, element: WebElement) -> None:
        script = "arguments[0].scrollIntoView();"
        self.driver.execute_script(script, element)


class CookieChoice(BaseNavigation):
    """Represents cookie consent overlay"""

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
        super().__init__(driver, visual_mode)

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

        except SE.NoSuchElementException:
            logging.info("cookie consent modal was not found")
        return cookie_overlay

    def _is_visible(self) -> bool:
        """Check cookie consent overlay visibility

        Returns
        -------
        bool
        """
        cookie_overlay = self._overlay_cookie_consent
        if cookie_overlay is not None:
            return cookie_overlay.is_displayed()
        else:
            return False

    def reject_non_essential_cookies(self):
        """Chooses to reject non essential cookies and dismisses the overlay"""
        if self._is_visible():
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

    def accept_all_cookies(self):
        """Chooses to accept all cookies and dismisses the overlay"""
        if self._is_visible():
            btn_accept_all_cookies = self.find(
                (
                    By.XPATH,
                    "//div[contains(@class, 'cookies')]//descendant::button[@data-test='button-submitCookie']",
                ),
            )
            btn_accept_all_cookies.click()


class PracujplMainPage(BaseNavigation):
    """Models pracuj.pl home page"""

    def __init__(self, driver, visual_mode=False, reject_cookies=False) -> None:
        """

        Parameters
        ----------
        driver : WebDriver
            selenium webdriver object
        visual_mode: bool
            decides whether all newly found elements will get highlighted
            for human inspection
        reject_cookies : bool
            when True: causes non-essential cookies to be rejected
            on visiting the homepage
            when False: causes all cookies to be accepted
        """
        super().__init__(driver, visual_mode)
        self.visit("https://www.pracuj.pl")
        if reject_cookies:
            CookieChoice(driver, visual_mode).reject_non_essential_cookies()
        else:
            CookieChoice(driver, visual_mode).accept_all_cookies()
        self._search_bar_box = [
            None,
            (
                By.XPATH,
                "//div[@data-test='section-search-bar' or @data-test='section-search-bar-it']",
            ),
        ]

        self._btn_search_submit = [
            None,
            (
                By.XPATH,
                ".//descendant::div[@data-test='section-search-with-filters' or @data-test='section-search-with-filters-it']/button",
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
                "mid_regular": "//descendant::div[@data-test='select-option-4']",
                "senior": "//descendant::div[@data-test='select-option-18']",
                "expert": "//descendant::div[@data-test='select-option-19']",
                "manager": "//descendant::div[@data-test='select-option-5']",
                "director": "//descendant::div[@data-test='select-option-6']",
                "president": "//descendant::div[@data-test='select-option-21']",
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
                "o_zastepstwo": "//descendant::div[@data-test='select-option-4']",
                "agencyjna": "//descendant::div[@data-test='select-option-5']",
                "o_prace_tymczasowa": "//descendant::div[@data-test='select-option-6']",
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
                "full_office": "//descendant::div[@data-test='select-option-full-office']",
                "hybrid": "//descendant::div[@data-test='select-option-hybrid']",
                "home_office": "//descendant::div[@data-test='select-option-home-office']",
                "mobile": "//descendant::div[@data-test='select-option-mobile']",
            },
        )
        self._search_field = [
            None,
            (
                By.XPATH,
                ".//descendant::label[contains(text(), 'Stanowisko, firma, słowo kluczowe') or contains(text(), 'Посада, компанія, ключове слово')]/preceding-sibling::input[@data-test='input-field']",
            ),
        ]
        self._category_field = [
            None,
            (
                By.XPATH,
                ".//descendant::label[contains(text(), 'Kategoria') or contains(text(), 'Категорія')]/preceding-sibling::input[@data-test='input-field']",
            ),
        ]
        self._location_field = [
            None,
            (
                By.XPATH,
                ".//descendant::label[contains(text(), 'Lokalizacja') or contains(text(), 'Розташування')]/preceding-sibling::input[@data-test='input-field']",
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
            logging.error("couldn't find search mode selector")
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
                logging.error(f"unknown search mode {mode}, valid: 'default', 'it'")
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
        self.search_field.send_keys(Keys.ENTER)

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
            logging.error("couldn't find distance dropdown")
            raise e
        return dist_dropdown

    @property
    def _distance(self) -> Distance:
        try:
            d_filed = self.find(
                (By.XPATH, ".//descendant::input[@data-test='input-field' and @value]"),
                root_element=self._distance_dropdown,
            )
            str_d_value = d_filed.get_attribute("value")
        except SE.NoSuchElementException as e:
            logging.error("couldn't find distance dropdown")
            raise e
        # example str_d_value looks like this: "+30 km"
        m = re.match(r"^\+(?P<dist>[0-9]*)\skm$", str_d_value)
        for dist in list(Distance):
            if int(m["dist"]) == dist.value:
                return dist
        else:
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
        if self._search_bar_box[0] is None:
            try:
                self._search_bar_box[0] = self.find(
                    self._search_bar_box[1],
                )
            except SE.NoSuchElementException as e:
                logging.critical("search box was not found")
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
        if control[0] is None:
            try:
                logging.warning(f"Looking for {control}")
                control[0] = self.find(control[1], root_element=self.search_bar_box)
            except SE.NoSuchElementException as e:
                logging.critical(f"{control[0]} was not found")
                raise e
        return control[0]