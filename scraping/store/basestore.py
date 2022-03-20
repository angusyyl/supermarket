from abc import ABC, abstractmethod
import datetime

class BaseStore(ABC):
    """Abstract base class for Store
    """
    def __init__(self, name, address, tel, opening_hours, lat, lng, created_ts=datetime.datetime.now(), updated_ts=datetime.datetime.now()):
        self.name = name
        self.address = address
        self.tel = tel
        self.opening_hours = opening_hours
        self.lat = lat
        self.lng = lng
        self.created_ts = created_ts
        self.updated_ts = updated_ts