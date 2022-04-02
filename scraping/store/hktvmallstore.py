from .basestore import BaseStore


class HKTVmallStore(BaseStore):
    def __init__(self, name, cat, address, area, district, opening_hours, frozen_pickup, chill_pickup, tel=None, lat=None, lng=None):
        super().__init__(name, address, area, district, tel, opening_hours, lat, lng)
        self.cat = cat
        self.frozen_pickup = frozen_pickup
        self.chill_pickup = chill_pickup

    def __repr__(self):
        return f'{type(self)}{self.__dict__}'
