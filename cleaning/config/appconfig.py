import os
from configparser import ConfigParser, ExtendedInterpolation


class AppConfig:
    config_path = os.path.join(
        '/home/angus/supermarket/cleaning/config', 'config.ini')
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read(config_path, 'utf-8')

    @staticmethod
    def get_config(key, section='PROJECT'):
        return AppConfig.config[section][key]