import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from selenium.webdriver.support.select import Select

from .basescraper import BaseScraper
from store.wellcomestore import WellcomeStore


class WellcomeScraper(BaseScraper):
    def __init__(self):
        super().__init__('WELLCOME', __name__)

    def _get_store_table_el(self):
        """Find the table WebElement having all the stores information such as store lat/lng, name, address, telephone and opening hours

        Returns:
            WebElement: A table WebElement of all stores
        """
        self.logger.debug('Start to wait to find all-store table')
        stores_el = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_element(
            By.CSS_SELECTOR, 'table.table.table-hover.table-striped>tbody'), 'Timedout to find stores table!')
        self.logger.debug('stores_el ref %s', stores_el)
        self.logger.debug('Found all-store table')

        return stores_el

    def _wait_for_store_table_stale(self, stores_el):
        """An explict wait for the store table element to be stale

        Args:
            stores_el (WebElement): The table WebElement of all stores

        Returns:
            boolean: The staleness of the given element
        """
        self.logger.debug(
            'Start to wait for last stores table element to be stale')
        self.logger.debug('stores_el ref %s', stores_el)
        result = WebDriverWait(self.driver, 30, 5).until(EC.staleness_of(
            stores_el), 'Timedout to wait for stores table element to be stale!')
        self.logger.debug(
            'Finished waiting for last stores table element to be stale')

        return result

    def scrape(self):
        try:
            self._scrape_store()
            self._scrape_product()
        finally:
            self._quitdriver()

    def _scrape_store(self):
        try:
            self.logger.info(
                f'Started web scraping stores of {self.supermarket}.')

            self._get(self.store_url_chi)

            # find stores table WebElement
            stores_el = self._get_store_table_el()

            # select area WebElement
            select_area_el = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_element(
                By.ID, 'edit-field-region-target-id--2'), 'Timedout to select area dropdownlist!')
            # select_area_el = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_element(By.CSS_SELECTOR, 'select.form-select:nth-of-type(1)'), 'Timedout to select area dropdownlist!')
            # select area object
            select_area_obj = Select(select_area_el)
            # a list[WebElement] of options that the select area WebElement contains
            select_area_opt_els = select_area_obj.options
            for i in range(1, len(select_area_opt_els)):
                area = select_area_opt_els[i].text
                select_area_obj.select_by_index(i)
                self._wait_for_store_table_stale(stores_el)
                stores_el = self._get_store_table_el()
                self.logger.info('------------%s------------', area)

                # select district WebElement
                select_dist_el = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_element(
                    By.ID, 'edit-tid--2'), 'Timedout to find select area dropdownlist!')
                # select_dist_el = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_element(By.CSS_SELECTOR, 'select.form-select:nth-of-type(2)'), 'Timedout to find select area dropdownlist!')
                # select district object
                select_dist_obj = Select(select_dist_el)
                # a list[WebElement] of options that the select district WebElement contains
                select_dist_opt_els = select_dist_obj.options
                for j in range(1, len(select_dist_opt_els)):
                    district = select_dist_opt_els[j].text
                    select_dist_obj.select_by_index(j)
                    self.logger.info('------------%s------------', district)

                    try:
                        self._wait_for_store_table_stale(stores_el)
                        stores_el = self._get_store_table_el()
                    except TimeoutException:
                        self.logger.exception(
                            'Cannot find stores table in %s in %s', district, area)
                        continue

                    row_els = stores_el.find_elements(By.CSS_SELECTOR, 'tr')
                    stores_cnt = len(row_els)
                    if not stores_cnt > 0:
                        self.logger.warning(
                            'Cannot find any stores in %s in %s', district, area)
                        continue
                    # row_els = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'table.table.table-hover.table-striped>tbody>tr')), 'Timedout to find table rows!')
                    self.logger.info('Found %d stores in %s in %s.',
                                     stores_cnt, district, area)

                    tr_num = 1
                    for row_el in row_els:
                        try:
                            lat_lng = row_el.find_element(
                                By.CSS_SELECTOR, '.views-field.views-field-title span.store-title').get_attribute('data-latlng')
                            if lat_lng is None:
                                raise NoSuchElementException
                            else:
                                lat = lat_lng.split('|')[0]
                                lng = lat_lng.split('|')[1]
                        except Exception:
                            lat_lng = None
                            self.logger.warning(
                                f'Cannot find the lat/lng of store in {district} in {area} at #{tr_num} <tr>.', exc_info=1)
                        try:
                            name = row_el.find_element(
                                By.CSS_SELECTOR, '.views-field.views-field-title span.store-title').text
                        except Exception:
                            name = None
                            self.logger.warning(
                                f'Cannot find the name of store in {district} in {area} at #{tr_num} <tr>.', exc_info=1)
                        try:
                            address = row_el.find_element(
                                By.CSS_SELECTOR, '.views-field.views-field-field-address').text
                        except Exception:
                            address = None
                            self.logger.warning(
                                f'Cannot find the address of store in {district} in {area} at #{tr_num} <tr>.', exc_info=1)
                        try:
                            tel = row_el.find_element(
                                By.CSS_SELECTOR, '.views-field.views-field-field-store-telephone').text
                        except Exception:
                            tel = None
                            self.logger.warning(
                                f'Cannot find the telephone of store in {district} in {area} at #{tr_num} <tr>.', exc_info=1)
                        try:
                            opening_hours = row_el.find_element(
                                By.CSS_SELECTOR, '.views-field.views-field-field-opening-hours').text
                        except Exception:
                            opening_hours = None
                            self.logger.warning(
                                f'Cannot find the opening hours of store in {district} in {area} at #{tr_num} <tr>.', exc_info=1)

                        store = WellcomeStore(
                            name, address, area, district, tel, opening_hours, lat, lng)
                        self.logger.info('Scraped store: {}'.format(store))
                        self.store_list.append(store)
                        tr_num = tr_num + 1                        
            self.logger.info('Scraped {} stores: {}.'.format(
                len(self.store_list), self.store_list))
            self.logger.info('Finished web scraping stores.')

            self._save_store_data()
        except:
            self.logger.exception('Error happened during web scraping stores!')

    def _scrape_product(self):
        pass
