from .baseproduct import BaseProduct
from util import dateutil


class CitySuperPdt(BaseProduct):
    def __init__(self, pdt_id, s_desc, price, img_url, detail_url=None, l_desc=None, is_out_of_stock=None, cat1=None, cat2=None, cat3=None):
        super().__init__(s_desc, price, img_url, l_desc, is_out_of_stock)
        self.cat1 = cat1
        self.cat2 = cat2
        self.cat3 = cat3
        self.pdt_id = pdt_id
        self.detail_url = detail_url
        self.img_url = img_url

    def __repr__(self):
        return 'CitySuperPdt(pdt_id="{}", cat1="{}", cat2="{}", cat3="{}", s_desc="{}", l_desc="{}", detail_url="{}", is_out_of_stock="{}", img_url="{}", price="{}", created_ts="{}", updated_ts="{}")'.format(
            self.pdt_id, self.cat1, self.cat2, self.cat3, self.s_desc, self.l_desc, self.detail_url, self.is_out_of_stock, self.img_url, self.price, self.created_ts, self.updated_ts)
