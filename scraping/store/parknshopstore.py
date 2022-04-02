from .basestore import BaseStore


class ParknShopStore(BaseStore):
    def __init__(self, region, district, brand, name, address, tel, opening_hours, lat, lng):
        super().__init__(name, address, region, district, tel, opening_hours, lat, lng)
        self.brand = brand

    def __repr__(self):
        return f'{type(self)}{self.__dict__}'
