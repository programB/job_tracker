from __future__ import annotations

import logging
import platform
from datetime import datetime
from typing import TYPE_CHECKING

from selenium.common import exceptions as SE
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions

from .base_navigation import AdsPopup, BaseNavigation

if TYPE_CHECKING:
    from selenium.webdriver.remote.webelement import WebElement


class Advertisement(BaseNavigation):
    """Models a single advertisement on the results subpage"""

    def __init__(
        self,
        driver,
        root_element: WebElement | None = None,
        visual_mode=False,
    ):
        """

        Parameters
        ----------
        driver : WebDriver
            selenium webdriver object
        root_element : WebElement
            a tag from which to start looking for information
        visual_mode: bool
            decides whether all newly found elements will get highlighted
            for human inspection
        """
        super().__init__(driver, visual_mode)
        self.root_element = root_element
        self._offer_dict = {
            "id": 0,
            "link": "",
            "title": "",
            "salary": "",
            "company_id": 0,
            "company_name": "",
            "company_link": "",
            "job_level": "",
            "contract_type": "",
            "technology_tags": [],
            "publication_date": datetime(1, 1, 1),
            "webscrap_timestamp": datetime(1, 1, 1),
        }
        self.is_valid_offer = False
        self.is_multiple_location_offer = False
        self._build_dict()

    def _build_dict(
        self,
    ):  # noqa: E501 pylint: disable=locally-disabled, too-many-statements, too-many-branches
        """Extracts information under the root_element, fills _offer_dict"""

        # NOTE: Advertisement object is constructed by parsing child div
        # elements below the root_element passed (which is a box div element
        # holding all the offers). In this case all the offers are present
        # and visible and there should be no need to use any of the selenium
        # wait strategies to parse the contents of individual offers.
        try:
            top_div = self.root_element.find_element(
                By.XPATH,
                "./div[@data-test='default-offer' and @data-test-offerid and @data-test-location]",  # noqa: E501 pylint: disable=locally-disabled, line-too-long
            )
            self._offer_dict["id"] = top_div.get_attribute("data-test-offerid")
        except SE.NoSuchElementException:
            # There are commercial ads among genuine offers
            # that should be ignored
            logging.error("no valid offer found in div %s", self.root_element)
            self.is_valid_offer = False
            return

        try:
            company_link_element = top_div.find_element(
                By.XPATH,
                ".//descendant::div[@data-test='section-company']//descendant::a[@data-test='link-company-profile'][2]",  # noqa: E501 pylint: disable=locally-disabled, line-too-long
            )
        except (SE.NoSuchElementException, ValueError, AttributeError):
            logging.warning(
                "offer doesn't seem to provide company information, offer skipped"
            )
            return
        else:
            if company_link_element is not None:
                company_link = company_link_element.get_attribute("href")
                self._offer_dict["company_link"] = company_link
                self._offer_dict["company_id"] = int(company_link.split("/")[-1])
                self._offer_dict["company_name"] = company_link_element.find_element(
                    By.XPATH, "./h4"
                ).text

        try:
            match top_div.get_attribute("data-test-location"):
                case "single":
                    self.is_multiple_location_offer = False
                case "multiple":
                    self.is_multiple_location_offer = True
                case _:
                    raise RuntimeError
        except RuntimeError:
            logging.warning("unknown offer type (neither single nor multiple)")

        try:
            link = top_div.find_element(By.XPATH, "./div/a").get_attribute(
                "href"
            )  # noqa: E501
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
            self._offer_dict["title"] = top_div.find_element(
                By.XPATH,
                search_xpath,
            ).text
        except SE.NoSuchElementException as webelement_not_found:
            # Everything should have a title!
            # We should give up here
            logging.warning("_offer_dict: %s", self._offer_dict)
            logging.warning("offer does not have a title")
            raise webelement_not_found

        try:
            self._offer_dict["salary"] = top_div.find_element(
                By.XPATH,
                ".//descendant::span[@data-test='offer-salary']",
            ).text
        except SE.NoSuchElementException:
            # Some genuine offers do not provide salary information, it's OK.
            self._offer_dict["salary"] = "not specified"
            logging.warning("offer does not provide salary information")

        try:
            self._offer_dict["company_name"] = top_div.find_element(
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
            self._offer_dict["job_level"] = top_div.find_element(
                By.XPATH,
                ".//descendant::li[@data-test='offer-additional-info-0']",
            ).get_attribute("innerText")
            # ).text
            # the text property isn't working as the text has some
            # pseudo selectors eg:
            # <li class="mobile-hidden tiles_iwlrcdk"
            #     data-test="offer-additional-info-0">
            # Specjalista (Mid / Regular)
            # ::after
            # </li>
        except SE.NoSuchElementException:
            # Unusual but acceptable
            logging.warning("offer does not provide job level information")

        try:
            self._offer_dict["contract_type"] = top_div.find_element(
                By.XPATH,
                ".//descendant::li[@data-test='offer-additional-info-1']",
            ).get_attribute("innerText")
        except SE.NoSuchElementException:
            # Unusual but acceptable
            logging.warning("offer does not provide contract type information")

        try:
            pub_date_str = top_div.find_element(
                By.XPATH,
                ".//descendant::p[@data-test='text-added']",
            ).get_attribute("innerText")
        except SE.NoSuchElementException:
            logging.warning("offer does not provide publication date, offer skipped")
            return
        else:
            try:
                months_pl = {
                    "stycznia": 1,
                    "lutego": 2,
                    "marca": 3,
                    "kwietnia": 4,
                    "maja": 5,
                    "czerwca": 6,
                    "lipca": 7,
                    "sierpnia": 8,
                    "września": 9,
                    "października": 10,
                    "listopada": 11,
                    "grudnia": 12,
                }
                months_ua = {
                    "січня": 1,
                    "лютого": 2,
                    "березня": 3,
                    "квітня": 4,
                    "травня": 5,
                    "червня": 6,
                    "липня": 7,
                    "серпня": 8,
                    "вересня": 9,
                    "жовтня": 10,
                    "листопада": 11,
                    "грудня": 12,
                }
                # date_parts has different size depending on language (pl: 3, ua: 4)
                date_parts = pub_date_str.strip().split(":")[1].strip().split(" ")
                d, m_str, y = [date_parts[i] for i in (0, 1, 2)]
                m = (months_pl | months_ua)[m_str.lower()]
                self._offer_dict["publication_date"] = datetime(int(y), m, int(d))
            except Exception as e:
                logging.error(
                    "failed to parse publication date, offer skipped. Explanaition %s",
                    str(e),
                )
                return

        # find_all (using find_elements) does not raise any exceptions
        # but returns empty list if no matching tags are found
        # hence if..else
        if tech_tags_elements := self.find_all(
            (
                By.XPATH,
                ".//descendant::span[@data-test='technologies-item']",
            ),
            root_element=top_div,
        ):
            for tag in tech_tags_elements:
                # If an offer has many tags those that do not fit
                # on a single line get hidden by JS. In those cases
                # they are being found by the selector above but the
                # tag.text property returns empty string !
                # tag.get_attribute("innerText") works as expected.
                self._offer_dict["technology_tags"].append(
                    tag.get_attribute("innerText")
                )
        else:
            logging.warning("offer does not provide technology tags")
        #
        # finally the timestamp
        self._offer_dict["webscrap_timestamp"] = datetime.utcnow()
        # if the code reaches this point it means this is a valid job offer
        self.is_valid_offer = True

    @property
    def id(self) -> int:
        """Unique offer id

        0 means invalid offer
        """
        return self._offer_dict["id"]

    @property
    def link(self) -> str:
        """URL to the offer's details

        empty string if URL not provided
        """
        return self._offer_dict["link"]

    @property
    def title(self) -> str:
        """Offer's title"""
        return self._offer_dict["title"]

    @property
    def salary(self) -> str:
        """Offered salary

        empty string if salary not specified
        """
        return self._offer_dict["salary"]

    @property
    def company_id(self) -> int:
        """Unique company id

        0 means company id couldn't be found
        """

        return self._offer_dict["company_id"]

    @property
    def company_name(self) -> str:
        """Name of the company offering the job"""

        return self._offer_dict["company_name"]

    @property
    def company_link(self) -> str:
        """URL to the page with company details

        empty string if URL not provided
        """

        return self._offer_dict["company_link"]

    @property
    def job_level(self) -> str:
        """Job level for the offer

        Can be a comma separated list.
        Job levels names usually come from
        a list predefined by pracuj.pl
        (however this is not guaranteed to always be the case):
        - trainee
        - assistant
        - junior
        - mid_regular
        - senior
        - expert
        - manager
        - director
        - president
        - laborer
        """
        return self._offer_dict["job_level"]

    @property
    def contract_type(self) -> str:
        """Contract type for the offer

        Contract type names usually come from
        a list predefined by pracuj.pl
        (however this is not guaranteed to always be the case):
        - o_prace
        - o_dzielo
        - zlecenie
        - B2B
        - o_zastepstwo
        - agencyjna
        - o_prace_tymczasowa
        - praktyki
        """
        return self._offer_dict["contract_type"]

    @property
    def technology_tags(self) -> list[str]:
        """Technology tags specified in the offer

        These are known to exist only for IT offers when search mode
        is set to 'it'. A tag can be a programming language eg. 'JavaScript'
        or specific application candidates are expected to be familiar with
        eg. 'Jira'

        Returns
        -------
        list[str]
        """
        return self._offer_dict["technology_tags"]

    @property
    def webscrap_timestamp(self) -> datetime:
        """Date and time when the offer was scraped from the webpage

        0001-01-01T00:00:00 denotes incorrect value
        """
        return self._offer_dict["webscrap_timestamp"]

    @property
    def publication_date(self) -> datetime:
        """Date and time when the offer was (re)published on the webpage

        0001-01-01T00:00:00 denotes incorrect value
        """
        return self._offer_dict["publication_date"]


class ResultsPage(BaseNavigation):
    """Class modeling the page with the search results"""

    def __init__(
        self,
        driver,
        visual_mode=False,
        attempt_closing_popups=True,
    ) -> None:
        super().__init__(driver, visual_mode)
        if attempt_closing_popups:
            AdsPopup(driver, visual_mode).close()

    @property
    def tot_no_of_subpages(self) -> int:
        """Total number of subpages as reported by the webpage

        Returns
        -------
        int
        """
        try:
            tot_locator = (
                By.XPATH,
                "//span[@data-test='top-pagination-max-page-number']",
            )
            tot_no_element = self.wait_with_timeout.until(
                expected_conditions.visibility_of_element_located(tot_locator),
            )
        except (SE.NoSuchElementException, SE.TimeoutException):
            logging.warning("Total number of subpages couldn't be established")
            return 0
        return int(tot_no_element.text)

    @property
    def subpage_offers(self) -> list[Advertisement]:
        """Produces a list of valid job offers from the current subpage

        Offers will be a valid job offers (not other ads)
        Offers ARE NOT guaranteed to be unique.

        Returns
        -------
        list[Advertisement]
        """
        sp_offers = []
        offers_section = self.wait_with_timeout.until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, "//div[@data-test='section-offers']"),
            )
        )
        all_child_divs = self.find_all(
            (By.XPATH, "./div"),
            root_element=offers_section,
        )
        logging.warning("len(all_child_divs): %s", len(all_child_divs))
        for child_div in all_child_divs:
            ad = Advertisement(self.driver, child_div)
            if ad.is_valid_offer:
                sp_offers.append(ad)
        return sp_offers

    @property
    def all_offers(self) -> list[Advertisement]:
        """Produces a list of unique offers from all subpages

        Returns
        -------
        list[Advertisement]
        """
        offers = []
        for page in range(1, self.tot_no_of_subpages + 1):
            if page != self.get_current_subpage()[1]:
                self.goto_subpage(n=page)
            offers.extend(self.subpage_offers)
        # Some offers are repeated on consecutive subpages
        # de-duplicate the list before returning
        unique_offers = []
        for offer in offers:
            if all((offer.id != u_offer.id for u_offer in unique_offers)):
                unique_offers.append(offer)
        del offers
        return unique_offers

    def get_current_subpage(self) -> tuple[WebElement | None, int]:
        """Current subpage as found in the input field on the website

        If the input field is found on the webpage associated WebElement,
        is returned as well as the numerical value of the subpage itself.

        Returns
        -------
        tuple[WebElement | None, int]
            if the input field is found its WebElement is returned and its
            value attribute (subpage number)
            if not found (None,0) is returned.
            (valid subpage numbering always starts from 1)
        """
        try:
            csb_element = self.find(
                (By.XPATH, "//input[@name='top-pagination']"),
            )
        except SE.NoSuchElementException:
            logging.warning("Current subpage number couldn't be established")
            return (None, 0)
        return (csb_element, int(csb_element.get_attribute("value")))

    def goto_subpage(self, n: int) -> None:
        """Switch to a subpage

        Parameters
        ----------
        n : int
            subpage number to go to

        Raises
        ------
        RuntimeError if the element controlling page switching cannot be found
        ValueError on attempt to switch to a subpage outside the
        range given by tot_no_of_subpages
        """
        page_field, page_no = self.get_current_subpage()
        if page_field is None:
            raise RuntimeError(
                f"could not switch to subpage {n}, \
            page selector not found"
            )

        tot_no_of_subpages = self.tot_no_of_subpages
        if (page_no == 0) or (page_no > tot_no_of_subpages):
            raise ValueError(
                f"failed to switch to not existing subpage no. {n}, \
            there are only {tot_no_of_subpages} subpages"
            )

        actions = ActionChains(self.driver)
        mod_key = (
            Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL
        )  # noqa: E501
        # Clear the field by ctrl+a and Delete,
        #   (page_field.clear() doesn't work and page_field always gets
        #    automatically set to '1' - page's JavaScript is doing this)
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
