from .baseproduct import BaseProduct
from util import dateutil


class CitySuperPdt(BaseProduct):
    def __init__(self, s_desc, price, cat1, img_url, l_desc, detail_url, pdt_id, cat2, is_out_of_stock=False, img=None, cat3=None):
        """Constructor

        Args:
            s_desc (str): The short description.
            price (str): The price with currency symbol, if any.
            cat1 (str): The main product category to which the product item belongs.
            img_url (str): The url which a later batch download process uses to fetch and store the product image.
            l_desc (str): The full description.
            detail_url (str): The url of the product item page.
            pdt_id (str): An unique product id which may be found from the DOM of the scraped website.
            cat2 (str): The 2nd-level product category.
            is_out_of_stock (bool, optional): Indicator of the availability. True if the product item cannot be added to the basket. Defaults to False.
            img (str, optional): The stored image path locally. Defaults to None.
            cat3 (str, optional): The 3rd-level product category. Defaults to None.
        """
        super().__init__(s_desc, price, cat1, img_url, l_desc, detail_url, is_out_of_stock, img)
        self.pdt_id = pdt_id
        self.cat2 = cat2
        self.cat3 = cat3

    def __repr__(self):
        return f'{type(self)}{self.__dict__}'