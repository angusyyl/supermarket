from .basestore import BaseStore


class MarketPlaceStore(BaseStore):
    def __init__(self, area, district, name, address, tel, opening_hours, lat, lng, remarks):
        super().__init__(name, address, area, district, tel, opening_hours, lat, lng)
        self.remarks = remarks

    def __repr__(self):
        return f'{type(self)}{self.__dict__}'
