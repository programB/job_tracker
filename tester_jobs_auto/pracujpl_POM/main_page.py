import logging
from typing import Tuple

from selenium.common import exceptions as SE
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .base_navigation import BaseNavigation


class OptionsMenu:
    def __init__(
        self,
        # driver: WebDriver,
        driver,
        main_locator: Tuple[str, str],
        btn_rel_locator: str,
        option_rel_locators: dict,
    ) -> None:
        self.driver = driver
        self._main_locator = main_locator
        self._btn_rel_locator = btn_rel_locator
        self._option_locators = option_rel_locators

    @property
    def menu(self) -> WebElement:
        return self.driver.find_element(
            self._main_locator[0],
            self._main_locator[1] + self._btn_rel_locator,
        )

    def select(self, options: list[str]) -> None:
        for option in options:
            if option in self._option_locators.keys():
                try:
                    # unfold menu
                    self.menu.click()
                    element = self.driver.find_element(
                        self._main_locator[0],
                        self._main_locator[1] + self._option_locators[option],
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
        if option in self._option_locators.keys():
            try:
                # unfold menu
                self.menu.click()
                element = self.driver.find_element(
                    self._main_locator[0],
                    self._main_locator[1] + self._option_locators[option],
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


class PracujplMainPage(BaseNavigation):
    def __init__(self, driver, visual_mode=False, reject_cookies=False) -> None:
        super().__init__(driver, visual_mode)
        self.reject_cookies = reject_cookies
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
        self.employment_type = OptionsMenu(
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

    def gohome(self):
        self.visit("https://www.pracuj.pl")
        if self.reject_cookies:
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
                logging.warning(f"Looking for {control}")
                # control[0] = self.search_bar_box.find_element(*control[1])
                control[0] = self.find(control[1], root_element=self.search_bar_box)
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
