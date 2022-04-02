import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from .basescraper import BaseScraper
from store.parknshopstore import ParknShopStore
from util import fileutil


class ParknshopScraper(BaseScraper):
    def __init__(self):
        super().__init__('PARKNSHOP', __name__)

    def _get_list_of_store_divs(self):
        """Find the list of div WebElements having all the stores information such as lat/lng, store name, brand, address, telephone and opening hours

        Returns:
            WebElement: A list of div WebElements of all stores
        """
        self.logger.debug('Start to wait to find all-store divs')
        div_els = WebDriverWait(self.driver, 30, 5).until(lambda d: d.find_elements(
            By.CSS_SELECTOR, 'div.shop-list>div.iscroll-object>div.scroll>div.location-info'), 'Timedout to find store divs!')
        self.logger.debug('stores_el_list ref %s', div_els)
        self.logger.debug('Found all store divs')

        return div_els

    def _queue_up(self):
        """Wait until the queue finished.
        """
        # while WebDriverWait(self.driver, 30, 5).until(lambda d: d.findElement(By.CSS_SELECTOR, '#lbHeaderH2')):
        while 'queue' in self.driver.current_url:
            time.sleep(10)
            self.logger.info('In the queue. Sleep for 10 seconds.')

    def _scrape_store(self):
        try:
            self.logger.info(
                f'Started web scraping stores of {self.supermarket}.')

            self._get(self.store_url_chi)

            self._queue_up()

            # find the list[WebElement] of store divs
            try:
                div_els = self._get_list_of_store_divs()
            except TimeoutException as te:
                self.logger.exception('{} screenshot dumped at {}.'.format(
                    te.msg, fileutil.dump_screenshot(self.driver, 'err_parknshop_scraping')))
                raise

            for i in range(0, len(div_els)):
                dlv_el = div_els[i]
                try:
                    region = dlv_el.get_attribute('data-region')
                    if region is None:
                        raise NoSuchElementException
                except Exception:
                    region = None
                    self.logger.warning(
                        'Cannot find the region of store at #%d <div>.', i + 1)
                try:
                    district = dlv_el.get_attribute('data-district')
                    if region is None:
                        raise NoSuchElementException
                except Exception:
                    district = None
                    self.logger.warning(
                        'Cannot find the district of store at #%d <div>.', i + 1)
                try:
                    brand = dlv_el.get_attribute('data-brandname')
                    if brand is None:
                        raise NoSuchElementException
                except Exception:
                    brand = None
                    self.logger.warning(
                        'Cannot find the brand of store at #%d <div>.', i + 1)
                try:
                    parking = dlv_el.get_attribute('data-parking')
                    if parking is None:
                        raise NoSuchElementException
                except Exception:
                    parking = False
                    self.logger.warning(
                        'Cannot find the parking of store at #%d <div>.', i + 1)
                try:
                    lat = dlv_el.get_attribute('data-latitude')
                    if lat is None:
                        raise NoSuchElementException
                except Exception:
                    lat = None
                    self.logger.warning(
                        'Cannot find the lat of store at #%d <div>.', i + 1)
                try:
                    lng = dlv_el.get_attribute('data-longitude')
                    if lng is None:
                        raise NoSuchElementException
                except Exception:
                    lng = None
                    self.logger.warning(
                        'Cannot find the lng of store at #%d <div>.', i + 1)
                try:
                    name = dlv_el.find_element(
                        By.CSS_SELECTOR, 'div.detail>div.info>p.shop-name').get_attribute('innerText')
                except Exception:
                    name = None
                    self.logger.warning(
                        'Cannot find the name of store at #%d <div>.', i + 1)
                try:
                    address = dlv_el.find_element(
                        By.CSS_SELECTOR, 'div.detail>div.info>p.address').get_attribute('innerText')
                except Exception:
                    address = None
                    self.logger.warning(
                        'Cannot find the address of store at #%d <div>.', i + 1)
                try:
                    opening_hours = dlv_el.find_element(
                        By.CSS_SELECTOR, 'div.detail>div.info>p.opening-hour').get_attribute('innerText').strip()
                except Exception:
                    opening_hours = None
                    self.logger.warning(
                        'Cannot find the opening_hours of store at #%d <div>.', i + 1)
                try:
                    tel = dlv_el.find_element(
                        By.CSS_SELECTOR, 'div.detail>div.info>div.phone').get_attribute('innerText').strip()
                except Exception:
                    tel = None
                    self.logger.warning(
                        'Cannot find the tel of store at #%d <div>.', i + 1)

                store = ParknShopStore(
                    region, district, brand, name, address, tel, opening_hours, lat, lng)
                self.logger.info('Scraped store: {}'.format(store))
                self.store_list.append(store)

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
