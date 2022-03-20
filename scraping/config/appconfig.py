import os
from configparser import ConfigParser, ExtendedInterpolation


class AppConfig:
    config_path = os.path.join(
        '/home/angus/supermarket/scraping/config', 'config.ini')
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read(config_path, 'utf-8')

    @staticmethod
    def get_config(key, section='PROJECT'):
        return AppConfig.config[section][key]

    @staticmethod
    def undef():
        """Return a hardcoded value 'UNDEF' to identify the value of a scraped data cannot be fetched successfully.

        Returns:
            str: A hardcoded value 'UNDEF'.
        """
        return 'UNDEF'

    @staticmethod
    def get_driver_max_retry():
        return int(AppConfig.get_config('DRIVER_MAX_GET_RETRY'))