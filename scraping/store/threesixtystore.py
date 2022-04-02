from .basestore import BaseStore


class ThreeSixtyStore(BaseStore):
    def __init__(self, name, address, tel, opening_hours, lat, lng, area=None, district=None):
        super().__init__(name, address, area, district, tel, opening_hours, lat, lng)

    def __repr__(self):
        return f'{type(self)}{self.__dict__}'
