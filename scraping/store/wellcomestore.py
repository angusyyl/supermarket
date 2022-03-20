from .basestore import BaseStore
from util import dateutil


class WellcomeStore(BaseStore):
    def __init__(self, name, address, tel, opening_hours, lat, lng, remarks, area, district):
        super().__init__(name, address, tel, opening_hours, lat, lng)
        self.remarks = remarks
        self.area = area
        self.district = district

    def __repr__(self):
        return 'WellcomeStore(name="{}", address="{}", tel="{}", opening_hours="{}", lat="{}", lng="{}", remarks="{}", area="{}", district="{}", created_ts="{}", updated_ts="{}")'.format(
            self.name, self.address, self.tel, self.opening_hours, self.lat, self.lng, self.remarks, self.area, self.district, dateutil.str_of_dt_dmYHMS(self.created_ts), dateutil.str_of_dt_dmYHMS(self.updated_ts))
