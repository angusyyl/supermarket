import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from selenium.webdriver.support.select import Select

from .basescraper import BaseScraper
from store.marketplacestore import MarketPlaceStore


class MarketPlaceScraper(BaseScraper):
    def __init__(self):
        super().__init__('MARKETPLACE', __name__)

    def _get_district_select_el(self):
        """Find the select WebElement dropdown for district

        Returns:
            WebElement: A select WebElement for district
        """
        self.logger.debug('Start to wait to find district select')
        district_sel_el = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_element(
            By.CSS_SELECTOR, '[id^="edit-field-district-value"]'), 'Timedout to find select district dropdownlist!')
        self.logger.debug('district_sel_el ref %s', district_sel_el)
        self.logger.debug('Found district select dropdown list')

        return district_sel_el

    def _wait_for_district_select_stale(self, district_sel_el):
        """An explict wait for the district select element to be stale

        Args:
            district_sel_el (WebElement): The select WebElement for district

        Returns:
            boolean: The staleness of the given element
        """
        self.logger.debug(
            'Start to wait for last district select element to be stale')
        self.logger.debug('district_sel_el ref %s', district_sel_el)
        result = WebDriverWait(self.driver, 30, 5).until(EC.staleness_of(
            district_sel_el), 'Timedout to wait for district select element to be stale!')
        self.logger.debug(
            'Finished waiting for last district select element to be stale')

        return result

    def _get_area_select_el(self):
        """Find the select WebElement dropdown for area

        Returns:
            WebElement: A select WebElement for area
        """
        self.logger.debug('Start to wait to find area select')
        area_sel_el = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_element(
            By.CSS_SELECTOR, '[id^="edit-field-region-value"]'), 'Timedout to find area select dropdownlist!')
        self.logger.debug('area_sel_el ref %s', area_sel_el)
        self.logger.debug('Found area select dropdown list')

        return area_sel_el

    def _wait_for_area_select_stale(self, area_sel_el):
        """An explict wait for the area select element to be stale

        Args:
            area_sel_el (WebElement): The select WebElement for area

        Returns:
            boolean: The staleness of the given element
        """
        self.logger.debug(
            'Start to wait for last area select element to be stale')
        self.logger.debug('area_sel_el ref %s', area_sel_el)
        result = WebDriverWait(self.driver, 30, 5).until(EC.staleness_of(
            area_sel_el), 'Timedout to wait for area select element to be stale!')
        self.logger.debug(
            'Finished waiting for last area select element to be stale')

        return result

    def _get_store_table_el(self):
        """Find the table WebElement having all the stores information such as store lat/lng, name, address, telephone and opening hours

        Returns:
            WebElement: A table WebElement of all stores
        """
        self.logger.debug('Start to wait to find all-store table')
        stores_el = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_element(
            By.CSS_SELECTOR, 'table.table>tbody'), 'Timedout to find stores table!')
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

    def _get_geolocation_wrapper(self):
        """Returns geolocations of all stores.

        Returns:
            list: A list of dictionaries containing location Id as the key and latitude and longtitude in a tuple as the value
        """
        self.logger.info('Start to wait to find geolocation divs')
        store_loc_list = []
        loc_divs = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_elements(
            By.CSS_SELECTOR, 'div.geolocation-map-wrapper>div'), 'Timedout to find geolocation divs!')
        for div_el in loc_divs:
            loc_id = div_el.get_attribute('data-scroll-target-id')
            loc_lat = div_el.get_attribute('data-lat')
            loc_lng = div_el.get_attribute('data-lng')
            store_loc_list.append({loc_id: (loc_lat, loc_lng)})
        self.logger.debug('Store locations: {}'.format(store_loc_list))
        self.logger.info('Found geolocation divs')

        return store_loc_list

    def _scrape_store(self):
        try:
            self.logger.info(f'Started web scraping stores of {self.supermarket}.')
            
            self._get(self.store_url_chi)

            # find geolocation map wrapper
            store_loc_list = self._get_geolocation_wrapper()

            # find stores table WebElement
            stores_el = self._get_store_table_el()
            # select district WebElement
            select_dist_el = self._get_district_select_el()

            # select area WebElement
            select_area_el = self._get_area_select_el()
            # select area object
            select_area_obj = Select(select_area_el)
            # a list[WebElement] of options that the select area WebElement contains
            select_area_opt_els = select_area_obj.options
            area_opt_len = len(select_area_opt_els)
            for i in range(1, area_opt_len):
                area = select_area_opt_els[i].get_attribute('text')
                select_area_obj.select_by_index(i)
                self.logger.info('------------%s------------', area)
                self._wait_for_area_select_stale(select_area_el)
                self._wait_for_district_select_stale(select_dist_el)
                self._wait_for_store_table_stale(stores_el)
                stores_el = self._get_store_table_el()

                # select district WebElement
                select_dist_el = self._get_district_select_el()
                # select district object
                select_dist_obj = Select(select_dist_el)
                # a list[WebElement] of options that the select district WebElement contains
                select_dist_opt_els = select_dist_obj.options
                dist_opt_len = len(select_dist_opt_els)
                for j in range(1, dist_opt_len):
                    district = select_dist_opt_els[j].text
                    select_dist_obj.select_by_index(j)
                    self.logger.info('------------%s------------', district)

                    try:
                        # get re-rendered select district WebElement
                        self._wait_for_district_select_stale(select_dist_el)
                        select_dist_el = self._get_district_select_el()
                        select_dist_obj = Select(select_dist_el)
                        select_dist_opt_els = select_dist_obj.options
                    except TimeoutException:
                        self.logger.exception(
                            'Cannot find re-rendered select district in %s in %s', district, area)
                        raise

                    # this must be put after district (start)
                    try:
                        # get re-rendered select area WebElement
                        self._wait_for_area_select_stale(select_area_el)
                        select_area_el = self._get_area_select_el()
                        select_area_obj = Select(select_area_el)
                        select_area_opt_els.clear()
                        select_area_opt_els = select_area_obj.options
                    except TimeoutException:
                        if j == dist_opt_len - 1:
                            self.logger.exception(
                                'Cannot find re-rendered select area in %s in %s', district, area)
                            raise
                        else:
                            self.logger.warning(
                                'Cannot find re-rendered select area in %s in %s', district, area)
                    # this must be put after district (end)

                    try:
                        # get re-rendered store table WebElement
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
                    self.logger.info('Found %d stores in %s in %s.',
                                     stores_cnt, district, area)

                    tr_num = 1
                    for row_el in row_els:
                        try:
                            loc_id = row_el.find_element(
                                By.CSS_SELECTOR, '.views-field.views-field-title>a').get_attribute('href')
                            try:
                                loc_id = loc_id[loc_id.rindex('#')+1:]
                            except ValueError:
                                self.logger.exception(
                                    'Cannot find the # in href. Hence, cannot find the lat of store in %s in %s at #%d <tr>.', district, area, tr_num)

                            if loc_id is not None:
                                for loc_dict in store_loc_list:
                                    if loc_id in loc_dict:
                                        (lat, lng) = loc_dict[loc_id]
                                        break
                                try:
                                    lat
                                except NameError:
                                    lat = ''
                                    self.logger.warning(
                                        'Cannot find the lat of store in %s in %s at #%d <tr>.', district, area, tr_num)
                                try:
                                    lng
                                except NameError:
                                    lng = ''
                                    self.logger.warning(
                                        'Cannot find the lng of store in %s in %s at #%d <tr>.', district, area, tr_num)
                        except NoSuchElementException:
                            loc_id = ''
                            self.logger.warning(
                                'Cannot find the location Id of store in %s in %s at #%d <tr>.', district, area, tr_num)
                        try:
                            name = row_el.find_element(
                                By.CSS_SELECTOR, '.views-field.views-field-title').get_attribute('innerText')
                        except Exception:
                            name = ''
                            self.logger.warning(
                                'Cannot find the name of store in %s in %s at #%d <tr>.', district, area, tr_num)
                        try:
                            address = row_el.find_element(
                                By.CSS_SELECTOR, '.views-field.views-field-field-address').text
                        except Exception:
                            address = ''
                            self.logger.warning(
                                'Cannot find the address of store in %s in %s at #%d <tr>.', district, area, tr_num)
                        try:
                            tel = row_el.find_element(
                                By.CSS_SELECTOR, '.views-field.views-field-field-telephone').text
                        except Exception:
                            tel = ''
                            self.logger.warning(
                                'Cannot find the telephone of store in %s in %s at #%d <tr>.', district, area, tr_num)
                        try:
                            opening_hours = row_el.find_element(
                                By.CSS_SELECTOR, '.views-field.views-field-field-opening-hours').text
                        except Exception:
                            opening_hours = ''
                            self.logger.warning(
                                'Cannot find the opening hours of store in %s in %s at #%d <tr>.', district, area, tr_num)
                        try:
                            remarks = row_el.find_element(
                                By.CSS_SELECTOR, '.views-field.views-field-field-free-parking').text
                        except Exception:
                            remarks = ''
                            self.logger.warning(
                                'Cannot find the remarks of store in %s in %s at #%d <tr>.', district, area, tr_num)

                        store = MarketPlaceStore(
                            name, address, tel, opening_hours, lat, lng)
                        self.logger.info('Scraped store: {}'.format(store))
                        self.store_list.append(store)
                        tr_num += tr_num
                        
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