import logging
import time
import os
import threading

from selenium.webdriver.support.events import EventFiringWebDriver

from scraper.wellcome import WellcomeScraper
from scraper.parknshop import ParknshopScraper
from scraper.marketplace import MarketPlaceScraper
from scraper.threesixty import ThreeSixtyScraper
from scraper.citysuper import CitySuperScraper
from scraper.hktvmall import HKTVmallScraper
# from config.applistener import AppListener

# project_root = os.path.join(os.path.dirname(__file__), '..')
project_root = os.path.join(os.path.dirname(__file__))


def main():
    # create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # create console handler
    console_hldr = logging.StreamHandler()
    console_hldr.setLevel(logging.DEBUG)
    # create file handler
    file_hldr = logging.FileHandler(os.path.join(project_root, 'main.log'))
    file_hldr.setLevel(logging.INFO)
    # create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - [%(levelname)s] %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
    # add formatter to console_hldr and file_hldr
    console_hldr.setFormatter(formatter)
    file_hldr.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(console_hldr)
    logger.addHandler(file_hldr)

    scraper_list = [
        # ('MarketPlace', MarketPlaceScraper().scrape),
        ('ThreeSixty', ThreeSixtyScraper().scrape)
        # ('Wellcome', WellcomeScraper().scrape),
        # ('Parknshop', ParknshopScraper().scrape),
        # ('CitySuper', CitySuperScraper().scrape),
        # ('HKTVmall', HKTVmallScraper().scrape)
    ]
    thread_list = []

    logger.info('Program started.')

    try:
        for scraper in scraper_list:
            # driver = webdriver.Chrome(service=service, options=options)
            # logger.info('User agent: {}'.format(driver.execute_script("return navigator.userAgent")))
            thd = threading.Thread(target=scraper[1])
            thread_list.append(thd)
            thd.start()
            logger.info(f'Started thread - {scraper[0]}.')
            time.sleep(10)

            # driver = EventFiringWebDriver(webdriver.Chrome(service=service, options=options), AppListener())
            # with EventFiringWebDriver(webdriver.Chrome(service=service, options=options), AppListener()) as driver:
            # driver.maximize_window()

            # WellcomeScraper(driver).scrape()

            # ParknshopScraper(driver).scrape()

            # MarketPlaceScraper(driver).scrape()

            # ThreeSixtyScraper(driver).scrape()

            # CitySuperScraper(driver).scrape()

            # HKTVmallScraper(driver).scrape()

            # driver2 = webdriver.Chrome(service=service, options=options)
            # logger.info('User agent: {}'.format(driver2.execute_script("return navigator.userAgent")))
            # threesixty_thd = threading.Thread(target=ThreeSixtyScraper(driver2).scrape)
            # threesixty_thd.start()
            # logger.info('Started thread - ThreeSixty.')

            # threesixty_thd.join()
        for thd in thread_list:
            thd.join()
    except:
        logger.exception('Program finished with exceptions.')
    else:
        logger.info('Program finished successfully.')


if __name__ == '__main__':
    main()
