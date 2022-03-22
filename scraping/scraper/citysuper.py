from sys import exc_info
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

from config.appconfig import AppConfig
from .basescraper import BaseScraper
from store.citysuperstore import CitySuperStore
from util import fileutil
from product.citysuper import CitySuperPdt


class CitySuperScraper(BaseScraper):
    def __init__(self):
        super().__init__('CITYSUPER', __name__)
        self.cur_lang = None

    def _extract_imgurl(self, dirty_imgurl):
        """Get a cleansed image url.

        Args:
            dirty_imgurl (str): The value of 'data-srcset' attribute of image stored from website.

        Returns:
            str: A well formatted downloadable image url.
        """
        urls = dirty_imgurl.split(', ')
        return f'https:{[url for url in urls if "280x.jpg" in url or "280x.jpeg" in url or "280x.png" in url][0]}'[:-5]

    def _get_list_of_store_divs(self):
        self.logger.debug('Start to wait to find all-store divs')
        div_els = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_elements(
            By.CSS_SELECTOR, 'section.flexboxgrid-container.container-fluid.margin-bottom-20px div.col-lg-6.col-md-6:nth-of-type(2)'), 'Timedout to find stores <div>!')
        self.logger.debug('stores_el_list ref %s', div_els)
        self.logger.debug('Found all store divs')

        return div_els

    def switch_page_lang(self, fr_lang, to_lang):
        max_wait = 30
        sleep_time = 3
        while max_wait > 0:
            try:
                self.logger.info(
                    'Switching from {} to {}.'.format(fr_lang, to_lang))
                div_el = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, f'.wgcurrent.wg-li.{fr_lang}')), 'Timedout to click <div> to switch the page language!')
                self.logger.debug('tag name %s', div_el.tag_name)
                self.logger.debug(
                    'innerHtml %s', div_el.get_attribute('innerHTML'))
                div_el.click()
                # ActionChains(self.driver).move_to_element(div_el).click().perform()
                a_el = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(EC.element_to_be_clickable((
                    By.CSS_SELECTOR, f'#weglot-language-{to_lang}')), 'Timedout to click <a> to switch the page language!')
                self.logger.debug('tag name %s', a_el.tag_name)
                a_el.click()
                self.logger.info('Clicked to switch language.')
                # ActionChains(self.driver).move_to_element(a_el).click().perform()

                # FIXME change to use custom javascript call
                time.sleep(3)
                self.cur_lang = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_element(
                    By.CSS_SELECTOR, 'html'), 'Timedout to find <html>!').get_attribute('lang')
                if self.cur_lang != to_lang:
                    self.logger.warning(
                        f'Current page language {self.cur_lang} is not changed to {to_lang}.')
                    raise TimeoutException
                else:
                    self.logger.info('Language switched.')
                    return None
            except TimeoutException:
                max_wait = max_wait - sleep_time
                if max_wait <= 0:
                    self.logger.warning('Screenshot dumped at {}.'.format(
                        fileutil.dump_screenshot(self.driver, 'err_citysuper_scraping')))
                    raise TimeoutException(
                        'Waited for {} seconds it still cannot switch the language.'.format(max_wait))
                else:
                    self.logger.warning(
                        f'Wait for {sleep_time} seconds to refresh browser for retry.')
                    time.sleep(sleep_time)
                    self.driver.refresh()
                    self.logger.warning('Browser refreshed.')

    def _scrape_store(self):
        try:
            self.logger.info(
                f'Started web scraping stores of {self.supermarket}.')
            self._get(self.store_url_eng)

            self.cur_lang = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_element(
                By.CSS_SELECTOR, 'html'), 'Timedout to find <html>!').get_attribute('lang')
            self.logger.info(f'This page is in "{self.cur_lang}" language.')
            if self.cur_lang == 'en':
                self.switch_page_lang('en', 'tw')

            # find the list[WebElement] of store divs
            div_els = self._get_list_of_store_divs()

            for div_el in div_els:
                try:
                    name = div_el.find_element(
                        By.CSS_SELECTOR, 'h4.font-cormorant-garamond').text
                except:
                    name = None
                    self.logger.warning(
                        'Cannot find the name of store. Skipped to next.')
                    continue
                try:
                    address = div_el.find_element(
                        By.CSS_SELECTOR, 'p:nth-of-type(1)').text
                except:
                    address = None
                    self.logger.warning(
                        'Cannot find the address of store %s.', name)
                try:
                    if div_el.find_element(By.CSS_SELECTOR, 'p:nth-of-type(2) i').text in ['營業時間', 'Business Hours']:
                        try:
                            opening_hours = div_el.find_element(
                                By.CSS_SELECTOR, 'p:nth-of-type(2)>span').text
                        except NoSuchElementException:
                            opening_hours = div_el.find_element(
                                By.CSS_SELECTOR, 'p:nth-of-type(2)').get_attribute('innerText')
                    elif div_el.find_element(By.CSS_SELECTOR, 'p:nth-of-type(3) i').text in ['營業時間', 'Business Hours']:
                        opening_hours = div_el.find_element(
                            By.CSS_SELECTOR, 'p:nth-of-type(3)').text
                    else:
                        raise NoSuchElementException
                except:
                    opening_hours = None
                    self.logger.warning(
                        'Cannot find the opening_hours of store %s.', name)

                store = CitySuperStore(
                    name, address, None, opening_hours, None, None)
                self.logger.info('Scraped store: {}'.format(store))
                self.store_list.append(store)

            self.logger.info('Scraped {} stores: {}.'.format(
                len(self.store_list), self.store_list))
            self.logger.info('Finished web scraping stores.')

            self._save_store_data()
        except:
            self.logger.exception('Error happened during web scraping stores!')

    def _scrape_product_main(self, cat1, cat2, cat3):
        scraped_list = []

        # check if there are multiple pages
        try:
            no_of_pages = len(WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_elements(
                By.CSS_SELECTOR, 'div.pagination>span.page')))
        except TimeoutException:
            # only one page
            no_of_pages = 1

        self.logger.info(f'{no_of_pages} page(s) found.')

        pg1_window = self.driver.current_window_handle

        for pg in range(0, no_of_pages):
            if no_of_pages > 1 and pg != no_of_pages - 1:
                try:
                    # find the url of the next product page in the pagination
                    next_pg_href = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_element(
                        By.CSS_SELECTOR, 'div.pagination>span.next>a')).get_attribute('href')
                except TimeoutException:
                    self.logger.warning(
                        'More than one product pages but no next page url. Page skipped. Screenshot dumped at {}.'.format(fileutil.dump_screenshot(
                            self.driver, 'err_citysuper_scraping')))
                    continue
            # scroll to the bottom of the page to have lazy-loaded elements loaded
            # self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')

            pdt_div_els = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_elements(
                By.CSS_SELECTOR, 'div.new-grid.product-grid.collection-grid>div.grid-item.large-grid-item.grid-product'))
            for i in range(0, len(pdt_div_els)):
                pdt_div_el = pdt_div_els[i]
                # scroll the product element into view to have it loaded due to its lazy loading
                self.driver.execute_script(
                    "arguments[0].scrollIntoView();", pdt_div_el)
                # webdriver.ActionChains(self.driver).move_to_element(pdt_div_el).perform()

                try:
                    pdt_id = pdt_div_el.get_attribute(
                        'data-product-id')
                except:
                    pdt_id = None
                    self.logger.warning(
                        f'Cannot find the product id of the {i+1}th product information.', exc_info=1)
                try:
                    detail_url = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: pdt_div_el.find_element(
                        By.CSS_SELECTOR, 'div.grid-item__content>a.grid-item__link')).get_attribute('href')
                except:
                    detail_url = None
                    self.logger.warning(
                        f'Cannot find the detail url of the {i+1}th product information.', exc_info=1)
                try:
                    img_url = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: pdt_div_el.find_element(
                        By.CSS_SELECTOR, 'img.grid__image-contain')).get_attribute('data-srcset')
                    img_url = self._extract_imgurl(img_url)
                except:
                    img_url = None
                    self.logger.warning(
                        f'Cannot find the image url of the {i+1}th product information.', exc_info=1)
                try:
                    s_desc = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: pdt_div_el.find_element(
                        By.CSS_SELECTOR, 'div.grid-product__title')).get_attribute('innerText')
                except:
                    s_desc = None
                    self.logger.warning(
                        f'Cannot find the short description of the {i+1}th product information.', exc_info=1)
                try:
                    price = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: pdt_div_el.find_element(
                        By.CSS_SELECTOR, 'span.visually-hidden')).text
                except:
                    price = None
                    self.logger.warning(
                        f'Cannot find the price of the {i+1}th product information.', exc_info=1)

                if img_url is not None and pdt_id is not None:
                    try:
                        fileutil.download_img(
                            self.supermarket, img_url, pdt_id)
                    except:
                        self.logger.warning(
                            f'Failed to download {img_url}.', exc_info=1)

                pdt = CitySuperPdt(
                    pdt_id, s_desc, price, img_url, cat1=cat1, cat2=cat2, cat3=cat3, detail_url=detail_url)
                self.logger.info(
                    'Scraped product: {}.'.format(pdt))

                scraped_list.append(pdt)

            # navigate to the next product page, if any
            if no_of_pages > 1:
                if pg >= 1:
                    self.driver.close()
                    self.logger.info(f'Closed "page{pg + 1}_tab."')
                    self.driver.switch_to.window(pg1_window)
                if pg != no_of_pages - 1:
                    self.logger.info(f'Opened "page{pg + 2}_tab."')
                    self.driver.switch_to.new_window(f'page{pg + 2}_tab')
                    self._get(next_pg_href)

        return scraped_list

    def _scrape_product(self):
        try:
            self.logger.info(
                f'Started web scraping products of {self.supermarket}.')

            self._get(self.store_url_eng)

            self.cur_lang = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_element(
                By.CSS_SELECTOR, 'html'), 'Timedout to find <html>!').get_attribute('lang')
            self.logger.info(f'This page is in "{self.cur_lang}" language.')
            if self.cur_lang == 'en':
                self.switch_page_lang('en', 'tw')

            try:
                # find the menu
                cat1_item_els = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_elements(
                    By.CSS_SELECTOR, 'div.first-menu__scroller>li.first-menu-item.has-submenu'), 'Timedout to find <li>s!')
                self.logger.info('Found 1st-category menu itmes.')

                # menu categories to be scraped
                menu_categories = AppConfig.get_config(
                    'CITYSUPER_MENU_CAT_ENG', 'PRGM_CONFIG').split(self._MENU_SEPARATOR)
                menu_categories.extend(AppConfig.get_config(
                    'CITYSUPER_MENU_CAT_CHI', 'PRGM_CONFIG').split(self._MENU_SEPARATOR))
            except TimeoutException:
                self.logger.critical(
                    'Cannot find the 1st-category menu items. Program aborted. Screenshot dumped at {}.'
                    .format(fileutil.dump_screenshot(self.driver, 'err_citysuper_scraping')))
                raise

            # store the ID of the original window at 1st-category page for later
            cat1_window = self.driver.current_window_handle

            # find 1st-category menu items
            for cat1_item_el in cat1_item_els:
                try:
                    cat1_item_a_el = cat1_item_el.find_element(
                        By.CSS_SELECTOR, 'a.first-menu-item__link')
                except TimeoutException:
                    self.logger.warning(
                        'Cannot find the archor link of 1st-category menu item. Skipped to next.')
                    continue
                # scrape only those categories in scope
                cat1 = cat1_item_a_el.get_attribute('innerText')
                self.logger.debug('cat1: %s', cat1)

                if cat1 in menu_categories:
                    try:
                        cat2_item_a_els = cat1_item_el.find_elements(
                            By.CSS_SELECTOR, 'div.second-menu__content>div.second-menu__inner>li.second-menu-item>div.second-menu-item__title>a.second-menu-item__link')
                        for cat2_item_a_el in cat2_item_a_els:
                            cat2 = cat2_item_a_el.get_attribute('innerText')
                            self.logger.debug('cat2: %s', cat2)
                            cat2_href = cat2_item_a_el.get_attribute('href')
                            try:
                                self.driver.switch_to.new_window(
                                    'second_cat_tab')
                                self.logger.info(
                                    f'Opened new tab "second_cat_tab" for "{cat1}" - "{cat2}".')
                                self._get(cat2_href)
                                # store the ID of the original window at 2nd-category page for later
                                cat2_window = self.driver.current_window_handle

                                # start to scrape the product information
                                try:
                                    sec_cat_div_el = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(
                                        lambda d: d.find_element(By.CSS_SELECTOR, 'div#shopify-section-subcats'))
                                    try:
                                        # find the list of "View All" <a> WebElement
                                        view_all_a_els = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(
                                            lambda d: d.find_elements(By.CSS_SELECTOR, 'a.btn.subcat-cta'))
                                        cat3_hrefs = [a.get_attribute(
                                            'href') for a in view_all_a_els]
                                        cat3_title_els = sec_cat_div_el.find_elements(
                                            By.CSS_SELECTOR, 'div.h3.section-header__title.subcat-title')
                                        # go to 3rd-category product page
                                        for i in range(0, len(cat3_hrefs)):
                                            cat3_pdt_list = []
                                            cat3 = cat3_title_els[i].get_attribute(
                                                'innerText')
                                            self.driver.switch_to.new_window(
                                                'third_cat_tab')
                                            self.logger.info(
                                                f'Opened new tab "third_cat_tab" for "{cat1}" - "{cat2}" - "{cat3}".')
                                            self._get(cat3_hrefs[i])
                                            try:
                                                self.logger.info(
                                                    'Scraping in 3rd-category product page.')

                                                cat3_pdt_list = self._scrape_product_main(
                                                    cat1, cat2, cat3)

                                                self.logger.info(
                                                    f'Scraped {len(cat3_pdt_list)} {cat3} products at 3rd category page.')
                                                self.pdt_list.extend(
                                                    cat3_pdt_list)
                                            finally:
                                                self.driver.close()
                                                self.logger.info(
                                                    'Closed "third_cat_tab".')
                                                self.driver.switch_to.window(
                                                    cat2_window)
                                    except TimeoutException:
                                        # if there is no "View All" button found, there should be some problems
                                        # take a screenshot for later investigation
                                        # continue to scrape next product
                                        self.logger.warning('No "View All" button found in {} - {}. Screenshot dumped at {}.'.format(
                                            cat1, cat2, fileutil.dump_screenshot(self.driver, 'err_citysuper_scraping')))
                                        continue
                                    except Exception as ex:
                                        self.logger.warning('Error happened: {} Screenshot dumped at {}.'.format(
                                            ex, fileutil.dump_screenshot(self.driver, 'err_citysuper_scraping')))
                                        self.logger.info('Continue to next 2nd-category.')
                                        continue
                                except TimeoutException:
                                    try:
                                        sec_cat_div_el = WebDriverWait(self.driver, type(self)._DRIVER_TIMEOUT, type(self)._DRIVER_TIMEOUT).until(lambda d: d.find_element(
                                            By.CSS_SELECTOR, 'div.new-grid.product-grid.collection-grid'))

                                        self.logger.info(
                                            'Scraping in 2nd-category product page.')

                                        cat2_pdt_list = self._scrape_product_main(
                                            cat1, cat2, None)
                                        self.logger.info(
                                            f'Scraped {len(cat2_pdt_list)} {cat2} products at 2nd category page.')
                                        self.pdt_list.extend(
                                            cat2_pdt_list)
                                    except TimeoutException:
                                        # if there is no product grid found, there should be some problems
                                        # take a screenshot for later investigation
                                        # continue to scrape next product
                                        self.logger.warning('No product grid found in {} - {}. Screenshot dumped at {}.'.format(
                                            cat1, cat2, fileutil.dump_screenshot(self.driver, 'err_citysuper_scraping')))
                                        continue
                                    except Exception as ex:
                                        self.logger.warning('Error happened: {} Screenshot dumped at {}.'.format(
                                            ex, fileutil.dump_screenshot(self.driver, 'err_citysuper_scraping')))
                                        self.logger.info('Continue to next 2nd-category.')
                                        continue
                            finally:
                                self.driver.close()
                                self.logger.info('Closed "second_cat_tab".')
                                self.driver.switch_to.window(cat1_window)
                    except TimeoutException:
                        self.logger.critical(
                            'Cannot find any archor links of 2nd-category menu items. Program aborted. Screenshot dumped at {}.'
                            .format(fileutil.dump_screenshot(self.driver, 'err_citysuper_scraping')))
                        raise

                    # make an incremental save of the products to avoid data loss in case of program aborted
                    self._save_pdt_data()
                    self.logger.info(f'Saved product data of {cat1}.')
                else:
                    self.logger.info(f'Skipped category {cat1}.')
                    continue

            self.logger.info('Scraped {} products: {}.'.format(
                len(self.pdt_list), self.pdt_list))
            self.logger.info('Finished web scraping products.')
        except:
            self.logger.exception(
                'Error happened during web scraping products!')

    def scrape(self):
        try:
            self._scrape_store()
            self._scrape_product()
        finally:
            self._quitdriver()
