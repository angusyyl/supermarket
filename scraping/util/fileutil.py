import os
import urllib.request

import jsonpickle

from config.appconfig import AppConfig
from util import dateutil
from util import strutil


def jsonpickle_w(output_file, py_obj):
    """Write the python object as json data.

    Args:
        output_file (str): The output file location looked up by the search key in config.ini.
        py_obj (Any): A python object to be serialized to json object.
        config_sec (str, optional): The configuration section in which the key is searched in config.ini. Defaults to 'DATA'.
    """
    with open(output_file, 'w') as data_file:
        data_file.write(jsonpickle.encode(py_obj, indent=4))


def dump_screenshot(driver, filename):
    """Dump a screenshot to app-configured directory.

    Args:
        driver (WebDriver): Chrome Webdriver.
        filename (str): The prefix of filename of the screenshot.

    Returns:
        str: The full filepath of the stored screenshot.
    """
    dir = os.path.join(
        AppConfig.get_config('SCREENSHOTS_LOG_DIR', 'LOG'),
        dateutil.str_of_now_Ymd())
    os.makedirs(dir, exist_ok=True)
    fullpath = os.path.join(dir, strutil.concat(
        filename, '-', dateutil.str_of_now_YmdHMS(), '.png'))
    driver.save_screenshot(fullpath)
    return fullpath


def download_img(supermarket, url, pdt_id):
    """Download the product image with associated product id.

    Args:
        supermarket (str): Supermarket name.
        url (str): Image url.
        pdt_id (str): The value of 'data-product-id' attribute extracted from website.
        
    Returns:
        str: The full filepath of the stored product image.
    """
    # ext = url[url.rindex('.'):]
    dir = os.path.join(AppConfig.get_config(f'{supermarket}_IMG_DATA', 'DATA'))
    os.makedirs(dir, exist_ok=True)
    saved_loc = os.path.join(dir, pdt_id)
    urllib.request.urlretrieve(url, saved_loc)[0]
    return saved_loc
