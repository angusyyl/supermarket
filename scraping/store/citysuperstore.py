from .basestore import BaseStore


class CitySuperStore(BaseStore):
    def __init__(self, name, address, opening_hours, district=None, area=None, tel=None, lat=None, lng=None):
        super().__init__(name, address, area, district, tel, opening_hours, lat, lng)

    def __repr__(self):
        return f'{type(self)}{self.__dict__}'
