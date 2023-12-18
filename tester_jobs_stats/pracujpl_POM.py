import logging
import time
from typing import Tuple

from selenium.common import exceptions as SE
# from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


class BaseNavigation:
    def __init__(self, driver) -> None:
        # self.driver: WebDriver = driver
        self.driver = driver
        self._timeout_sec = 5
        self._wait = WebDriverWait(self.driver, timeout=self._timeout_sec)

    @property
    def timeout_sec(self):
        return self._timeout_sec

    @timeout_sec.setter
    def timeout_sec(self, value):
        self._timeout_sec = value
        self._wait = WebDriverWait(self.driver, timeout=self._timeout_sec)

    def visit(self, url: str) -> None:
        try:
            self.driver.get(url)
        except Exception as e:
            logging.warning(f"problem visiting the page at: {url}")
            if "ERR_NAME_NOT_RESOLVED" in str(e):
                raise ConnectionError
            else:
                raise e

    def find(self, element, highlight: bool = False) -> WebElement:
        element_found = self.driver.find_element(*element)
        if highlight:
            self._highlight(element_found)
        return element_found

    def click(self, element: WebElement) -> None:
        element.click()

    def enter_text(self, element: WebElement, text: str) -> None:
        element.send_keys(text)

    def is_displayed(self, locator: Tuple[str, str]) -> bool:
        try:
            self._wait.until(
                expected_conditions.visibility_of_element_located(locator),
            )
            return True
        except SE.TimeoutException:
            logging.warning(f"Timeout of {self.timeout_sec}s reached while waiting for {locator}")
            return False

    def _highlight(self, element: WebElement):
        self.driver.execute_script(
            "arguments[0].style.backgroundColor='red'",
            element,
        )
        time.sleep(1)
