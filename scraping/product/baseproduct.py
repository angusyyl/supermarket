from abc import ABC, abstractmethod
from util import dateutil


class BaseProduct(ABC):
    """Abstract base class for Product
    """

    def __init__(self, s_desc, price, img, l_desc=None, is_out_of_stock=None, created_ts=dateutil.dt_of_now(), updated_ts=dateutil.dt_of_now()):
        self.s_desc = s_desc
        self.l_desc = l_desc
        self.price = price
        self.img = img
        self.is_out_of_stock = is_out_of_stock
        self.created_ts = created_ts
        self.updated_ts = updated_ts
