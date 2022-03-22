from .basestore import BaseStore
from util import dateutil


class ParknShopStore(BaseStore):
    def __init__(self, name, brand, address, tel, opening_hours, lat, lng, region, district):
        super().__init__(name, address, tel, opening_hours, lat, lng)
        self.brand = brand
        self.region = region
        self.district = district

    def __repr__(self):
        return 'ParknShopStore(name="{}", brand="{}", address="{}", tel="{}", opening_hours="{}", lat="{}", lng="{}", region="{}", district="{}", created_ts="{}", updated_ts="{}")'.format(
            self.name, self.brand, self.address, self.tel, self.opening_hours, self.lat, self.lng, self.region, self.district, self.created_ts, self.updated_ts)
