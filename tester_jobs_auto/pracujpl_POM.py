import json
import logging
import platform
import time
from typing import Tuple

from selenium.common import exceptions as SE
from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

    def find(self, element, root_element: WebElement | None = None, highlight_color: str | None = None) -> WebElement:
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


class Advertisement:
    def __init__(self, root_element: WebElement) -> None:
        self.root_element = root_element
        self._offer_dict = {
            "id": 0,
            "link": "",
            "title": "",
            "salary": "",
            "company_name": "",
            "job_level": "",
            "contract_type": "",
            "technology_tags": [],
            "webscrap_timestamp": 0.0,
        }
        self.is_valid_offer = False
        self.is_multiple_location_offer = False
        self._build_dict()

    def _build_dict(self):
        try:
            default_offer_div = self.root_element.find_element(
                By.XPATH,
                "./div[@data-test='default-offer' and @data-test-offerid and @data-test-location]",
            )
            self._offer_dict["id"] = default_offer_div.get_attribute("data-test-offerid")
        except SE.NoSuchElementException as webelement_not_found:
            # There are commercial ads among genuine offers
            # that should be ignored
            logging.error(f"no valid offer found in the div {self.root_element}")
            self.is_valid_offer = False
            return

        try:
            match default_offer_div.get_attribute("data-test-location"):
                case "single":
                    self.is_multiple_location_offer = False
                case "multiple":
                    self.is_multiple_location_offer = True
                case _:
                    raise RuntimeError
        except RuntimeError:
            logging.warning("unknown offer type (neither single nor multiple)")

        try:
            link = default_offer_div.find_element(By.XPATH, "./div/a").get_attribute("href")
            self._offer_dict["link"] = link
        except SE.NoSuchElementException:
            # Some job offers advertise the same position in multiple
            # physical locations to choose from.
            # Multiple links are exposed by the JavaScript creating a
            # new tag on user click event.
            # In such a case it's OK not to store the link at all
            # as its a non essential piece of information (offer id is)
            logging.warning("offer does not provide a link")

        try:
            if self.is_multiple_location_offer:
                search_xpath = ".//descendant::h2[@data-test='offer-title']"
            else:
                # search_xpath = ".//h2[@data-test='offer-title']/a"
                search_xpath = ".//descendant::h2[@data-test='offer-title']/a"
            self._offer_dict["title"] = default_offer_div.find_element(
                By.XPATH,
                search_xpath,
            ).text
        except SE.NoSuchElementException as webelement_not_found:
            # Everything should have a title!
            # We should give up here
            logging.warning(f"_offer_dict: {self._offer_dict}")
            logging.warning("offer does not have a title")
            raise webelement_not_found

        try:
            self._offer_dict["salary"] = default_offer_div.find_element(
                By.XPATH,
                ".//descendant::span[@data-test='offer-salary']",
            ).text
        except SE.NoSuchElementException:
            # Some genuine offers do not provide salary information, it's OK.
            self._offer_dict["salary"] = "not specified"
            logging.warning("offer does not provide salary information")

        try:
            self._offer_dict["company_name"] = default_offer_div.find_element(
                By.XPATH,
                ".//descendant::*[@data-test='text-company-name']",
            ).text
        except SE.NoSuchElementException:
            # If there is no company name that is probably an ad
            # that should be skipped
            logging.warning("offer does not provide company name")
            self.is_valid_offer = False
            return

        try:
            self._offer_dict["job_level"] = default_offer_div.find_element(
                By.XPATH,
                ".//descendant::li[@data-test='offer-additional-info-0']",
            ).get_attribute("innerText")
            # ).text
            # the text property isn't working as the text has some
            # pseudoselectors eg:
            # <li class="mobile-hidden tiles_iwlrcdk" data-test="offer-additional-info-0">
            # Specjalista (Mid / Regular)
            # ::after
            # </li>
        except SE.NoSuchElementException:
            # Unusual but acceptable
            logging.warning("offer does not provide job level information")

        try:
            self._offer_dict["contract_type"] = default_offer_div.find_element(
                By.XPATH,
                ".//descendant::li[@data-test='offer-additional-info-1']",
            ).get_attribute("innerText")
        except SE.NoSuchElementException:
            # Unusual but acceptable
            logging.warning("offer does not provide contract type information")

        # TODO: this requires selecting only IT offers on the main page
        #      as generic offers do not contain technology tags
        # try:
        #     tech_tags_elements = technology_tags_div.find_elements(
        #         By.XPATH,
        #         ".//descendant::span[@data-test='technologies-item']",
        #     )
        #     for tag in tech_tags_elements:
        #         self._offer_dict["technology_tags"].append(tag.text)
        # except SE.NoSuchElementException:
        #     logging.warning("offer does not provide technology tags")
        #
        # finalny the timestamp
        self._offer_dict["webscrap_timestamp"] = time.time()
        # if the code reaches this point it means this is a valid job offer
        self.is_valid_offer = True

    @property
    def id(self) -> int:
        return self._offer_dict["id"]

    @property
    def link(self) -> str:
        return self._offer_dict["link"]

    @property
    def title(self) -> str:
        return self._offer_dict["title"]

    @property
    def salary(self) -> str:
        return self._offer_dict["salary"]

    @property
    def company_name(self) -> str:
        return self._offer_dict["company_name"]

    @property
    def job_level(self) -> str:
        return self._offer_dict["job_level"]

    @property
    def contract_type(self) -> str:
        return self._offer_dict["contract_type"]

    @property
    def technology_tags(self) -> list[str]:
        return self._offer_dict["technology_tags"]

    @property
    def webscrap_timestamp(self) -> float:
        return self._offer_dict["webscrap_timestamp"]

    def to_json(self):
        return json.dumps(self._offer_dict)


class ResultsPage(BaseNavigation):
    """docstring for ResultsPage."""

    def __init__(self, driver, visual_mode=False):
        super(ResultsPage, self).__init__(driver, visual_mode)

    def current_subpage(self) -> tuple[WebElement | None, int]:
        try:
            csb_element = self.find((By.XPATH, "//input[@name='top-pagination']"))
        except SE.NoSuchElementException:
            logging.warning("Current subpage number couldn't be established")
            return (None, 0)
        else:
            return (csb_element, int(csb_element.get_attribute("value")))

    @property
    def tot_no_of_subpages(self) -> int:
        try:
            tot_no_element = self.find(
                (By.XPATH, "//span[@data-test='top-pagination-max-page-number']"),
            )
        except SE.NoSuchElementException:
            logging.warning("Total number of subpages couldn't be established")
            return 0
        else:
            return int(tot_no_element.text)

    @property
    def total_offer_count(self):
        # TODO: Implement
        pass

    @property
    def subpage_offers(self) -> list[Advertisement]:
        sp_offers = []
        offers_section = self.find(
            (By.XPATH, "//div[@data-test='section-offers']"),
        )
        all_child_divs = offers_section.find_elements(By.XPATH, "./div")
        logging.warning(f"len(all_child_divs): {len(all_child_divs)}")
        for child_div in all_child_divs:
            ad = Advertisement(child_div)
            if ad.is_valid_offer:
                sp_offers.append(ad)
        return sp_offers

    def goto_subpage(self, n: int) -> None:
        page_field, _ = self.current_subpage()
        actions = ActionChains(self.driver)
        mod_key = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL
        if page_field is not None:
            # Clear the field by ctrl+a and Delete,
            #   (page_field.clear() doesn't work and page_field always gets
            #    automatically set to '1' - probably page's js is doing this)
            # then enter and submit the desired subpage number
            # fmt: off
            actions.key_down(mod_key).send_keys_to_element(page_field, "a") \
                .send_keys_to_element(page_field, Keys.DELETE).key_up(mod_key)\
                .send_keys_to_element(page_field, str(n)) \
                .send_keys_to_element(page_field, Keys.ENTER) \
                .perform()
            # fmt: on
            # page_field.clear()
            # page_field.send_keys(n)
            # page_field.send_keys(Keys.ENTER)
        else:
            raise RuntimeError(f"could not switch to subpage {n}, page selector not found")

    @property
    def all_offers(self) -> list[Advertisement]:
        offers = []
        for page in range(1, self.tot_no_of_subpages + 1):
            if page != self.current_subpage()[1]:
                self.goto_subpage(n=page)
            offers.extend(self.subpage_offers)
        return offers
