import time
import requests
import json

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException, TimeoutException
from bs4 import BeautifulSoup

from .basescraper import BaseScraper
from store.threesixtystore import ThreeSixtyStore


class ThreeSixtyScraper(BaseScraper):
    def __init__(self):
        super().__init__('THREESIXTY', __name__)

    def _get_stores_div_el(self):
        """Find the div WebElement having all the stores information such as store lat/lng, name, address, telephone and opening hours

        Returns:
            WebElement: A div WebElement of all stores
        """
        self.logger.debug('Start to wait to find all-store div')
        stores_el = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_element(
            By.CSS_SELECTOR, 'div.contactus_content.col-sm-12'), 'Timedout to find stores div!')
        self.logger.debug('stores_el ref %s', stores_el)
        self.logger.debug('Found all-store div')

        return stores_el

    def _scrape_store(self):
        try:
            self.logger.info(
                f'Started web scraping stores of {self.supermarket}.')

            self._get(self.store_url_chi)

            # fetch the lat and lng of stores
            resp = requests.get(self.store_url_eng)
            soup = BeautifulSoup(resp.text, 'html.parser')
            script_content = soup.find(
                'script', type='application/json').string
            self.logger.debug(script_content)
            try:
                store_lat_lng = json.loads(script_content)['google_map']
                self.logger.debug(store_lat_lng)
            except:
                store_lat_lng = None
                self.logger.exception('Cannot find geolocation of stores.')

            store_len = len(WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_elements(
                By.CSS_SELECTOR, 'div.contactus_content.col-sm-12>strong'), 'Timedout to find stores <strong>!'))
            self.logger.debug('Number of stores found: %s', store_len)

            # find stores table WebElement
            for nth_store in range(1, store_len + 1):
                try:
                    # the nth-<p> element child of the div
                    nth_p = 1 + (7 * (nth_store - 1))
                    try:
                        name = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_element(
                            By.CSS_SELECTOR, f'div.contactus_content.col-sm-12>strong:nth-of-type({nth_store})'), 'Timedout to find stores <strong>!').get_attribute('innerText')
                    except Exception:
                        name = None
                        self.logger.warning(
                            f'Cannot find the name of {nth_store}th store.')
                    try:
                        address = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_element(
                            By.CSS_SELECTOR, f'div.contactus_content.col-sm-12>p:nth-of-type({nth_p})'), 'Timedout to find address <p>!').text
                    except Exception:
                        address = None
                        self.logger.warning(
                            f'Cannot find the address of {nth_store}th store.')
                    try:
                        tel = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_element(
                            By.CSS_SELECTOR, f'div.contactus_content.col-sm-12>p:nth-of-type({nth_p + 1})>a'), 'Timedout to find tel <p>!').text
                    except Exception:
                        tel = None
                        self.logger.warning(
                            f'Cannot find the tel of {nth_store}th store.')
                    try:
                        opening_hours = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_element(
                            By.CSS_SELECTOR, f'div.contactus_content.col-sm-12>p:nth-of-type({nth_p + 3})'), 'Timedout to find opening hours <p>!').text
                    except Exception:
                        opening_hours = None
                        self.logger.warning(
                            f'Cannot find the opening_hours of {nth_store}th store.')
                    if store_lat_lng is None:
                        lat = None
                        lng = None
                        self.logger.warning(
                            f'Cannot find the lat/lng of {nth_store}th store.')
                    else:
                        lat = store_lat_lng.get(str(nth_store))[1]
                        lng = store_lat_lng.get(str(nth_store))[0]

                    store = ThreeSixtyStore(
                        name, address, tel, opening_hours, lat, lng)
                    self.logger.info('Scraped store: {}'.format(store))
                    self.store_list.append(store)
                except TimeoutException:
                    self.logger.exception('Cannot find store information.')
                    raise

            self.logger.info('Scraped {} stores: {}.'.format(
                len(self.store_list), self.store_list))
            self.logger.info('Finished web scraping stores.')

            self._save_store_data()
        except:
            self.logger.exception('Error happened during web scraping stores!')

    def _scrape_product(self):
        pass

    def scrape(self):
        try:
            self._scrape_store()
            self._scrape_product()
        finally:
            self._quitdriver()
