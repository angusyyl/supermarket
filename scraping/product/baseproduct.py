from abc import ABC, abstractmethod
from util import dateutil


class BaseProduct(ABC):
    """Abstract base class for Product
    """
    
    def __init__(self, s_desc, price, cat1, img_url, l_desc, detail_url, is_out_of_stock=False, img=None):
        """Base Constructor

        Args:
            s_desc (str): The short description.
            price (str): The price with currency symbol, if any.
            cat1 (str): The main product category to which the product item belongs.
            img_url (str): The url which a later batch download process uses to fetch and store the product image.
            l_desc (str): The full description.
            detail_url (str): The url of the product item page.
            is_out_of_stock (bool, optional): Indicator of the availability. True if the product item cannot be added to the basket. Defaults to False.
            img (str, optional): The stored image path locally. Defaults to None.
        """
        self.s_desc = s_desc
        self.price = price
        self.cat1 = cat1
        self.img_url = img_url
        self.l_desc = l_desc
        self.detail_url = detail_url
        self.is_out_of_stock = is_out_of_stock
        self.img = img
        self.scraped_ts = dateutil.str_of_utcnow_YmdHMS()
