from .basestore import BaseStore
from util import dateutil


class MarketPlaceStore(BaseStore):
    def __repr__(self):
        return 'MarketPlaceStore(name="{}", address="{}", tel="{}", opening_hours="{}", lat="{}", lng="{}", created_ts="{}", updated_ts="{}")'.format(
            self.name, self.address, self.tel, self.opening_hours, self.lat, self.lng, self.created_ts, self.updated_ts)
