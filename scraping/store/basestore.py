from abc import ABC, abstractmethod

from util import dateutil


class BaseStore(ABC):
    """Abstract base class for Store
    """

    def __init__(self, name, address, area, district, tel, opening_hours, lat, lng):
        self.name = name
        self.address = address
        self.area = area
        self.district = district
        self.tel = tel
        self.opening_hours = opening_hours
        self.lat = lat
        self.lng = lng
        self.scraped_ts = dateutil.str_of_utcnow_YmdHMS()
