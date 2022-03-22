from .basestore import BaseStore
from util import dateutil


class HKTVmallStore(BaseStore):
    def __init__(self, name, cat, address, opening_hours, frozen_pickup, chill_pickup, area, district):
        super().__init__(name, address, None, opening_hours, None, None)
        self.cat = cat
        self.frozen_pickup = frozen_pickup
        self.chill_pickup = chill_pickup
        self.area = area
        self.district = district

    def __repr__(self):
        return 'HKTVmallStore(name="{}", cat="{}", address="{}", tel="{}", opening_hours="{}", frozen_pickup="{}", chill_pickup="{}", lat="{}", lng="{}", area="{}", district="{}", created_ts="{}", updated_ts="{}")'.format(
            self.name, self.cat, self.address, self.tel, self.opening_hours, self.frozen_pickup, self.chill_pickup, self.lat, self.lng, self.area, self.district, self.created_ts, self.updated_ts)
