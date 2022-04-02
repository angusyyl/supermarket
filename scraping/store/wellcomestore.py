from .basestore import BaseStore
from util import dateutil


class WellcomeStore(BaseStore):
    def __init__(self, name, address, area, district, tel, opening_hours, lat, lng):
        super().__init__(name, address, area, district, tel, opening_hours, lat, lng)

    def __repr__(self):
        return f'{type(self)}{self.__dict__}'
