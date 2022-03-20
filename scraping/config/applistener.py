import logging

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.events import AbstractEventListener

from .appconfig import AppConfig


class AppListener(AbstractEventListener):
    
    def after_navigate_to(self, url: str, driver) -> None:
        """
        Loads a web page in the current browser session within max attempts.
        """
        for i in range(0, AppConfig.get_driver_max_retry()):
            try:
                # super().get(url)
                # logging.info(f'Visited {url}.')
                logging.info('hello')
            except WebDriverException:
                logging.info('Retrying the url visit.')
                continue