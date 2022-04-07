from sys import exc_info
import os


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.select import Select

from config.appconfig import AppConfig
from .basescraper import BaseScraper
from store.hktvmallstore import HKTVmallStore
from util import fileutil
from product.hktvmall import HKTVmallPdt


class HKTVmallScraper(BaseScraper):
    def __init__(self):
        super().__init__('HKTVMALL', __name__)
        self.cur_lang = None

    def _get_nxt_pg_el(self):
        """Find the next page button in pagination.

        Returns:
            WebElement: An anchor link WebElement
        """
        self.logger.debug('Start to wait to find next page button')
        nxt_pg_el = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_element(
            By.CSS_SELECTOR, '#table_paginate>ul.pagination>#table_next'), 'Timedout to find category select dropdownlist!')
        self.logger.debug('nxt_pg_el ref %s', nxt_pg_el)
        self.logger.debug('Found next page button')

        return nxt_pg_el

    def _wait_for_nxt_pg_stale(self, nxt_pg_el):
        """An explict wait for the next page anchor link element to be stale

        Args:
            nxt_pg_el (WebElement): The select WebElement for category

        Returns:
            boolean: The staleness of the given element
        """
        self.logger.debug(
            'Start to wait for last next page anchor link element to be stale')
        self.logger.debug('nxt_pg_el ref %s', nxt_pg_el)
        result = WebDriverWait(self.driver, 30, 5).until(EC.staleness_of(
            nxt_pg_el), 'Timedout to wait for next page anchor link element to be stale!')
        self.logger.debug(
            'Finished waiting for last next page anchor link element to be stale')

        return result

    def _get_cat_select_el(self):
        """Find the select WebElement dropdown for category

        Returns:
            WebElement: A select WebElement for category
        """
        self.logger.debug('Start to wait to find category select')
        cat_sel_el = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_element(
            By.CSS_SELECTOR, '.filter.filter-category'), 'Timedout to find category select dropdownlist!')
        self.logger.debug('cat_sel_el ref %s', cat_sel_el)
        self.logger.debug('Found category select dropdown list')

        return cat_sel_el

    def _wait_for_cat_select_stale(self, cat_sel_el):
        """An explict wait for the category select element to be stale

        Args:
            cat_sel_el (WebElement): The select WebElement for category

        Returns:
            boolean: The staleness of the given element
        """
        self.logger.debug(
            'Start to wait for last category select element to be stale')
        self.logger.debug('cat_sel_el ref %s', cat_sel_el)
        result = WebDriverWait(self.driver, 30, 5).until(EC.staleness_of(
            cat_sel_el), 'Timedout to wait for category select element to be stale!')
        self.logger.debug(
            'Finished waiting for last category select element to be stale')

        return result

    def _get_area_select_el(self):
        """Find the select WebElement dropdown for area

        Returns:
            WebElement: A select WebElement for area
        """
        self.logger.debug('Start to wait to find area select')
        area_sel_el = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_element(
            By.CSS_SELECTOR, '#area-input'), 'Timedout to find area select dropdownlist!')
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
        """Find the table WebElement having all the stores information such as store area, name, address and opening hours

        Returns:
            WebElement: A table WebElement of all stores
        """
        self.logger.debug('Start to wait to find all-store table')
        stores_el = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_element(
            By.CSS_SELECTOR, 'table#table'), 'Timedout to find stores table!')
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

    def _scrape_store(self):
        try:
            self.logger.info(
                f'Started web scraping stores of {self.supermarket}.')

            self._get(self.store_url_chi)

            # find the table[WebElement] of store divs
            stores_el = self._get_store_table_el()

            # find the a[WebElement] of next page
            nxt_pg_el = self._get_nxt_pg_el()

            # select category WebElement
            select_cat_el = self._get_cat_select_el()
            # select category object
            select_cat_obj = Select(select_cat_el)
            # a list[WebElement] of options that the select category WebElement contains
            select_cat_opt_els = select_cat_obj.options
            cat_opt_len = len(select_cat_opt_els)

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

                # try:
                #     # get re-rendered store table WebElement
                #     self._wait_for_store_table_stale(stores_el)
                #     stores_el = self._get_store_table_el()
                # except TimeoutException:
                #     self.logger.exception(
                #         'Cannot find stores table in %s', area)
                #     continue

                try:
                    # get re-rendered next page WebElement
                    self._wait_for_nxt_pg_stale(nxt_pg_el)
                    nxt_pg_el = self._get_nxt_pg_el()
                except TimeoutException:
                    self.logger.exception(
                        'Cannot find next page in %s', area)
                    continue

                for j in range(1, cat_opt_len):
                    cat = select_cat_opt_els[j].get_attribute('text')
                    select_cat_obj.select_by_index(j)
                    self.logger.info('------------%s------------', cat)

                    # try:
                    #     # get re-rendered store table WebElement
                    #     self._wait_for_store_table_stale(stores_el)
                    #     stores_el = self._get_store_table_el()
                    # except TimeoutException:
                    #     self.logger.exception(
                    #         'Cannot find stores table of %s in %s', cat, area)
                    #     continue

                    try:
                        # get re-rendered next page WebElement
                        self._wait_for_nxt_pg_stale(nxt_pg_el)
                        nxt_pg_el = self._get_nxt_pg_el()
                    except TimeoutException:
                        self.logger.exception(
                            'Cannot find next page of %s in %s', cat, area)
                        continue

                    pg = 1
                    while True:
                        self.logger.info(f'Scraping page {pg}.')

                        row_els = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(
                            lambda d: stores_el.find_elements(By.CSS_SELECTOR, 'tr'))
                        self.logger.debug(f'Found {len(row_els)} row(s).')

                        for k in range(1, len(row_els)):
                            row_el = row_els[k]
                            col_els = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: row_el.find_elements(
                                By.CSS_SELECTOR, 'td'))

                            try:
                                district = col_els[0].text
                            except:
                                district = None
                                self.logger.warning(
                                    'Cannot find the district of store.', exc_info=1)
                            try:
                                name = col_els[1].text
                            except:
                                name = None
                                self.logger.exception(
                                    'Cannot find the name of store.', exc_info=1)
                            try:
                                address = col_els[2].text
                            except:
                                address = None
                                self.logger.exception(
                                    'Cannot find the address of store.', exc_info=1)
                            try:
                                opening_hours = col_els[3].text
                            except:
                                opening_hours = None
                                self.logger.exception(
                                    'Cannot find the opening_hours of store.', exc_info=1)
                            try:
                                frozen_pickup = col_els[4].text
                            except:
                                frozen_pickup = None
                                self.logger.exception(
                                    'Cannot find the frozen_pickup of store.', exc_info=1)
                            try:
                                chill_pickup = col_els[5].text
                            except:
                                chill_pickup = None
                                self.logger.exception(
                                    'Cannot find the chill_pickup of store.', exc_info=1)

                            store = HKTVmallStore(
                                name, cat, address, area, district, opening_hours, frozen_pickup, chill_pickup)
                            self.logger.info('Scraped store: {}'.format(store))
                            self.store_list.append(store)

                        if 'disabled' in nxt_pg_el.get_attribute('class'):
                            break
                        else:
                            nxt_pg_el.click()
                            pg = pg + 1

                            # try:
                            #     # get re-rendered store table WebElement
                            #     self._wait_for_store_table_stale(stores_el)
                            #     stores_el = self._get_store_table_el()
                            # except TimeoutException:
                            #     self.logger.exception(
                            #         'Cannot find stores table of %s in %s', cat, area)
                            #     continue

                            try:
                                # get re-rendered next page WebElement
                                self._wait_for_nxt_pg_stale(nxt_pg_el)
                                nxt_pg_el = self._get_nxt_pg_el()
                            except TimeoutException:
                                self.logger.exception(
                                    'Cannot find next page in %s in %s', district, area)
                                continue

            self.logger.info('Scraped {} stores: {}.'.format(
                len(self.store_list), self.store_list))
            self.logger.info('Finished web scraping stores.')

            self._save_store_data()
        except:
            self.logger.exception('Error happened during web scraping stores!')

    def _get_pagelen(self, text):
        """Extract the total number of pages of the product from the given text.

        Args:
            text (str): The pages text shown in website.

        Returns:
            int: The total number of pages.
        """
        return int(''.join([alphabet for alphabet in text if alphabet.isdigit()]))

    def _get_list_of_pdt_divs(self):
        self.logger.debug('Start to wait to find all-product divs')
        pdt_div_els = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_elements(
            By.CSS_SELECTOR, 'div.product-brief-list>span.product-brief-wrapper>div.product-brief'))
        self.logger.debug('Found all product divs')

        return pdt_div_els

    def _wait_for_pdt_divs_stale(self, pdt_div_els):
        """An explict wait for the all product div elements to be stale

        Args:
            pdt_div_els (WebElement): The list of div WebElement of all products

        Returns:
            boolean: The staleness of all the given elements
        """
        self.logger.debug(
            'Start to wait for last product div elements to be stale.')
        try:
            for pdt_div_el in pdt_div_els:
                WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(
                    EC.staleness_of(pdt_div_el))
                self.logger.debug('pdt_div_el ref %s', pdt_div_el)
        except TimeoutException:
            return False
        else:
            self.logger.debug(
                'Finished waiting for last product div elements to be stale.')
            return True

    def _scrape_product_main(self, cat1, cat2):
        scraped_list = []

        # check if there are multiple pages
        try:
            no_of_pages = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_element(
                By.CSS_SELECTOR, 'span.total')).get_attribute('innerText')
            no_of_pages = self._get_pagelen(no_of_pages)
        except:
            self.logger.warning('No total page number can be found. Page skipped. Screenshot dumped at {}.'.format(
                fileutil.dump_screenshot(self.driver, 'err_hktvmall_scraping')))
            return None

        self.logger.info(
            f'{str(no_of_pages)} page(s) found of {cat1} - {cat2}.')
        if not no_of_pages:
            self.logger.warning('Screenshot dumped at {}.'.format(
                fileutil.dump_screenshot(self.driver, 'err_hktvmall_scraping')))

        for pg in range(0, no_of_pages):
            try:
                pdt_div_els = self._get_list_of_pdt_divs()
            except:
                self.logger.exception(
                    f'Failed to get the list of product divs during scraping. Skipped page {pg + 1} in {cat1} - {cat2}.')
                continue
            no_of_pdts = len(pdt_div_els)
            self.logger.info(f'Found {no_of_pdts} products at page {pg + 1}.')
            for i in range(0, no_of_pdts):
                pdt_div_el = pdt_div_els[i]
                # scroll the product element into view to have it loaded due to its lazy loading
                self.driver.execute_script(
                    "arguments[0].scrollIntoView();", pdt_div_el)
                # webdriver.ActionChains(self.driver).move_to_element(pdt_div_el).perform()

                try:
                    pdt_id = pdt_div_el.get_attribute('data-id')
                except:
                    pdt_id = None
                    self.logger.warning(
                        f'Cannot find the product id of the {i+1}th product information.', exc_info=1)
                try:
                    detail_url = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: pdt_div_el.find_element(
                        By.CSS_SELECTOR, 'a')).get_attribute('href')
                except:
                    detail_url = None
                    self.logger.warning(
                        f'Cannot find the detail url of the {i+1}th product information.', exc_info=1)
                try:
                    img_url = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: pdt_div_el.find_element(
                        By.CSS_SELECTOR, 'div.square-wrapper>div.image-container>img')).get_attribute('src')
                except:
                    img_url = None
                    self.logger.warning(
                        f'Cannot find the image url of the {i+1}th product information.', exc_info=1)
                try:
                    s_desc = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: pdt_div_el.find_element(
                        By.CSS_SELECTOR, 'div.info-wrapper>div.upper-wrapper>div.brand-product-name')).get_attribute('innerText')
                except:
                    s_desc = None
                    self.logger.warning(
                        f'Cannot find the short description of the {i+1}th product information.', exc_info=1)
                try:
                    price = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: pdt_div_el.find_element(
                        By.CSS_SELECTOR, 'div.info-wrapper>div.lower-wrapper>div.price-label>div.price>span')).text
                except:
                    price = None
                    self.logger.warning(
                        f'Cannot find the price of the {i+1}th product information.', exc_info=1)

                if img_url is not None and pdt_id is not None:
                    try:
                        img = fileutil.download_img(
                            self.supermarket, img_url, pdt_id)
                    except:
                        self.logger.warning(
                            f'Failed to download {img_url}.', exc_info=1)

                pdt = HKTVmallPdt(s_desc, price, cat1, img_url,
                                  None, detail_url, pdt_id, cat2, img=img)
                self.logger.info(
                    'Scraped product: {}.'.format(pdt))

                scraped_list.append(pdt)

            # navigate to the next product page, if any
            try:
                # look for the 2nd next page button at the bottom of the page
                next_btn_el = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_elements(
                    By.CSS_SELECTOR, 'a.next-btn:not(.disable)'))[1]
                self.driver.execute_script(
                    "arguments[0].scrollIntoView();", next_btn_el)
                try:
                    # next_btn_el.click()
                    self.driver.execute_script(
                        "arguments[0].click();", next_btn_el)
                except:
                    self.logger.exception('Failed to click next page. Screenshot dumped at {}.'.format(
                        fileutil.dump_screenshot(self.driver, 'err_hktvmall_scraping')))
                    return scraped_list
            except TimeoutException:
                self.logger.info('No next page button found.')

            if not self._wait_for_pdt_divs_stale(pdt_div_els):
                self.logger.warning(
                    f'Failed to wait for last product div elements to be stale. Stopped scraping at page {pg + 1}.')
                return scraped_list

        return scraped_list

    def _scrape_product(self):
        try:
            self.logger.info(
                f'Started web scraping products of {self.supermarket}.')

            self._get(self.pdt_url_chi)

            self.cur_lang = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_element(
                By.CSS_SELECTOR, 'html'), 'Timedout to find <html>!').get_attribute('lang')
            self.logger.info(f'This page is in "{self.cur_lang}" language.')

            try:
                # find the menu
                cat1_item_div_els = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_elements(
                    By.CSS_SELECTOR, 'div.subnav>ul>li>div.submenu.supermarket'), 'Timedout to find <div>s!')
                self.logger.info('Found 1st-category menu itmes.')

                # menu categories to be scraped
                menu_categories = AppConfig.get_config(
                    'HKTVMALL_MENU_CAT_ENG', 'PRGM_CONFIG').split(self._MENU_SEPARATOR)
                menu_categories.extend(AppConfig.get_config(
                    'HKTVMALL_MENU_CAT_CHI', 'PRGM_CONFIG').split(self._MENU_SEPARATOR))
                self.logger.info(f'Scraping categories: {menu_categories}.')
            except TimeoutException:
                self.logger.critical(
                    'Cannot find the 1st-category menu items. Program aborted.')
                raise

            # menu categories to be skipped
            skip_menu_categories = AppConfig.get_config(
                'HKTVMALL_SKIP_CAT_ENG', 'PRGM_CONFIG').split(self._MENU_SEPARATOR)
            skip_menu_categories.extend(AppConfig.get_config(
                'HKTVMALL_SKIP_CAT_CHI', 'PRGM_CONFIG').split(self._MENU_SEPARATOR))
            self.logger.info(f'Skipped scraping categories: {skip_menu_categories}.')
            
            # store the ID of the original window at 1st-category page for later
            cat1_window = self.driver.current_window_handle

            # find 1st-category menu items
            for cat1_item_div_el in cat1_item_div_els:
                # scrape only those categories in scope
                cat1_item_a_el = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: cat1_item_div_el.find_element(
                    By.CSS_SELECTOR, 'div.title>a.link'))
                cat1 = cat1_item_a_el.get_attribute('innerText')
                cat1 = cat1.replace('全部', '', 1).replace('All', '', 1).strip()
                self.logger.debug('cat1: %s', cat1)

                if cat1 in menu_categories:
                    try:
                        cat1_pdt_list = []
                        cat2_item_a_els = cat1_item_div_el.find_elements(
                            By.CSS_SELECTOR, 'div.clearfix>div.submenu-nav>ul>li>a.link')
                        for cat2_item_a_el in cat2_item_a_els:
                            cat2 = cat2_item_a_el.get_attribute('innerText')
                            cat2 = cat2[:cat2.index('\n')].strip()
                            self.logger.debug('cat2: %s', cat2)
                            
                            if cat2 in skip_menu_categories:
                                self.logger.info(f'Skipped cat2: {cat2}.')
                                continue
                            cat2_href = cat2_item_a_el.get_attribute('href')
                            try:
                                self.driver.switch_to.new_window(
                                    'second_cat_tab')
                                self.logger.info(
                                    f'Opened new tab "second_cat_tab" for "{cat1}" - "{cat2}".')
                                self._get(cat2_href)

                                # start to scrape the product information
                                self.logger.info(
                                    'Scraping in 2nd-category product page.')

                                cat2_pdt_list = self._scrape_product_main(
                                    cat1, cat2)

                                self.logger.info(
                                    f'Scraped {len(cat2_pdt_list)} {cat2} products at 2nd category page.')
                                cat1_pdt_list.extend(cat2_pdt_list)
                                self.pdt_list.extend(cat2_pdt_list)
                            except:
                                self.logger.exception(
                                    f'Error happened during scraping the product info. Skipped category {cat2}.')
                            finally:
                                self.driver.close()
                                self.logger.info('Closed "second_cat_tab".')
                                self.driver.switch_to.window(cat1_window)
                                
                                # save the products after scraping each 2nd category to avoid data loss in case of program aborted
                                self._save_pdt_data(cat1_pdt_list, cat1, cat2)
                                self.logger.info(f'Saved product data of {cat1} - {cat2}.')
                    except TimeoutException:
                        self.logger.critical(
                            'Cannot find any archor links of 2nd-category menu items. Program aborted.')
                        raise
                else:
                    self.logger.info(f'Skipped category {cat1}.')
                    continue

            self.logger.info('Scraped {} products: {}.'.format(
                len(self.pdt_list), self.pdt_list))
            self.logger.info('Finished web scraping products.')
        except:
            self.logger.exception(
                'Error happened during web scraping products!')
        pass

    def _save_pdt_data(self, pdt_list, cat1, cat2):
        filename = os.path.join(AppConfig.get_config(
            f'{self.supermarket}_PDT_DATA', 'DATA'))
        dot_idx = filename.rfind('.')
        filename = filename[:dot_idx] + '_' + \
            cat1.replace('/', '') + '_' + \
                cat2.replace('/', '') + filename[dot_idx:]
        fileutil.jsonpickle_w(filename, pdt_list)
        self.logger.info('Dumped product data.')

    def scrape(self):
        try:
            # self._scrape_store()
            self._scrape_product()
        finally:
            self._quitdriver()
