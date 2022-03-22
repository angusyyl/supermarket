import logging
import os
import platform
import sys
from abc import ABC, abstractmethod, abstractstaticmethod

from selenium.common.exceptions import WebDriverException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from requests.exceptions import ConnectionError

from config.appconfig import AppConfig
from util import fileutil


class BaseScraper(ABC):
    """Abstract base class for web scraper.
    """

    _MENU_SEPARATOR = '|'
    _DRIVER_TIMEOUT = int(AppConfig.get_config('DRIVER_TIMEOUT'))
    _DRIVER_POLL_FREQ = int(AppConfig.get_config('DRIVER_POLL_FREQ'))

    def __init__(self, supermarket, scraper_module):
        self.supermarket = supermarket
        self.logger = self.__init_logger(scraper_module)
        self.driver = self.__init_driver()
        self.store_url_eng = AppConfig.get_config(
            f'{self.supermarket}_ENG', 'STORE_URLS')
        self.store_url_chi = AppConfig.get_config(
            f'{self.supermarket}_CHI', 'STORE_URLS')
        try:
            self.pdt_url_eng = AppConfig.get_config(
                f'{self.supermarket}_ENG', 'PRODUCT_URLS')
        except KeyError:
            self.pdt_url_eng = None
        try:
            self.pdt_url_chi = AppConfig.get_config(
                f'{self.supermarket}_CHI', 'PRODUCT_URLS')
        except KeyError:
            self.pdt_url_chi = None
        self.store_list = []
        self.pdt_list = []

    def __init_driver(self):
        ua = UserAgent().random
        self.logger.info(f'Generated user agent: {ua}.')
        
        options = webdriver.ChromeOptions()
        # this is necessary to make sure "switch lang" element clickable for CitySuper website
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--headless')
        # options.add_argument("--start-maximized")
        options.add_argument(f'user-agent={ua}')
        # options.add_argument(
        #     'User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36')
        try:
            service = Service(executable_path=ChromeDriverManager().install())
        except ConnectionError:
            self.logger.exception('Retry to use local chromedriver.')
            self.logger.info('Platform system: {}'.format(platform.system()))
            if platform.system() == 'Windows':
                # set HA coporate proxy
                service = Service(
                    executable_path=r'D:\supermarket\scraping\chromedriver_win.exe')
                options.add_extension(r'D:\BDAP\proxy_auth_plugin.zip')
            elif platform.system() == 'Linux':
                service = Service(
                    executable_path=os.path.join(AppConfig.get_config('ROOT_DIR'), 'chromedriver'))
            else:
                self.logger.critical('Unknown system platform!')
                sys.exit(
                    'Program aborted due to unable to identify system platform to configure chromedriver.')

        driver = webdriver.Chrome(service=service, options=options)
        self.logger.info('User agent in use: {}.'.format(
            driver.execute_script("return navigator.userAgent")))
        return driver

    def __init_logger(self, scraper_module, log_lv=logging.DEBUG):
        # create logger
        self.logger = logging.getLogger(scraper_module)
        self.logger.setLevel(log_lv)
        # create console handler
        console_hldr = logging.StreamHandler()
        console_hldr.setLevel(log_lv)
        # create file handler
        file_hldr = logging.FileHandler(
            AppConfig.get_config(f'{self.supermarket}_LOG', 'LOG'), mode='w')
        file_hldr.setLevel(logging.INFO)
        # create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - [%(levelname)s] %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
        # add formatter to console_hldr and file_hldr
        console_hldr.setFormatter(formatter)
        file_hldr.setFormatter(formatter)
        # add ch to logger
        self.logger.addHandler(console_hldr)
        self.logger.addHandler(file_hldr)

        return self.logger

    def _get(self, url):
        """Navigate to the given url with retry attempts.

        Args:
            url (str): A http URL.

        Returns:
            None: For a successful visit.
        """
        self.logger.info(f'Accessing {url}.')
        max_retry = AppConfig.get_driver_max_retry()
        for i in range(0, max_retry):
            try:
                self.driver.get(url)
            except WebDriverException:
                # give it a retry
                self.logger.warning('Retry the url navigation.', exc_info=1)
                continue
            else:
                self.logger.info(f'Visited {url}.')
                return None
        raise WebDriverException(f'Failed to visit {url} after {max_retry} retries.')

    def _quitdriver(self):
        if self.driver:
            self.driver.quit()

    @abstractstaticmethod
    def scrape(self):
        pass

    @abstractmethod
    def _scrape_store(self):
        pass

    def _save_store_data(self):
        fileutil.jsonpickle_w(os.path.join(AppConfig.get_config(
            f'{self.supermarket}_STORE_DATA', 'DATA')), self.store_list)
        self.logger.info('Dumped store data.')

    @abstractmethod
    def _scrape_product(self):
        pass

    def _save_pdt_data(self):
        fileutil.jsonpickle_w(os.path.join(AppConfig.get_config(
            f'{self.supermarket}_PDT_DATA', 'DATA')), self.pdt_list)
        self.logger.info('Dumped product data.')
