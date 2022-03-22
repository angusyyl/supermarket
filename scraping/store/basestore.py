from abc import ABC, abstractmethod
import datetime

from util import dateutil

class BaseStore(ABC):
    """Abstract base class for Store
    """
    def __init__(self, name, address, tel, opening_hours, lat, lng, created_ts=dateutil.str_of_utcnow_YmdHMS(), updated_ts=dateutil.str_of_utcnow_YmdHMS()):
        self.name = name
        self.address = address
        self.tel = tel
        self.opening_hours = opening_hours
        self.lat = lat
        self.lng = lng
        self.created_ts = created_ts
        self.updated_ts = updated_ts