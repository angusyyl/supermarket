import logging
from abc import ABC, abstractmethod

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, FloatType, BooleanType

from config.appconfig import AppConfig


class BaseCleaner(ABC):
    """Abstract base class for data cleaner.
    """
    spark = SparkSession.builder.appName('SuperMarketCleaner').getOrCreate()
    
    def __init__(self, supermarket, cleaner_module):
        self._supermarket = supermarket
        self._logger = self.__init_logger(cleaner_module)
        self._store_raw_data_dir = AppConfig.get_config(
            'STORE_SRC_DATA_DIR', 'DATA')
        self._pdt_raw_data_dir = AppConfig.get_config('PDT_SRC_DATA_DIR', 'DATA')
        self._store_schema = StructType([
            StructField('area', StringType(), True),
            StructField('district', StringType(), True),
            StructField('brand', StringType(), True),
            StructField('name', StringType(), True),
            StructField('address', StringType(), False),
            StructField('tel', StringType(), True),
            StructField('opening_hours', StringType(), True),
            StructField('lat', StringType(), True),
            StructField('lng', StringType(), True)
        ])
        self._pdt_schema = StructType([
            StructField('s_desc', StringType(), True),
            StructField('price', FloatType(), True),
            StructField('cat1', StringType(), True),
            StructField('img_url', StringType(), True),
            StructField('l_desc', StringType(), True),
            StructField('detail_url', StringType(), True),
            StructField('is_out_of_stock', BooleanType(), False),
            StructField('img', StringType(), True),
            StructField('scraped_ts', StringType(), True)
        ])

    def __init_logger(self, cleaner_module, log_lv=logging.DEBUG):
        # create logger
        self._logger = logging.getLogger(cleaner_module)
        self._logger.setLevel(log_lv)
        # create console handler
        console_hldr = logging.StreamHandler()
        console_hldr.setLevel(log_lv)
        # create file handler
        file_hldr = logging.FileHandler(
            AppConfig.get_config(f'{self._supermarket}_LOG', 'LOG'), mode='w')
        file_hldr.setLevel(logging.INFO)
        # create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - [%(levelname)s] %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
        # add formatter to console_hldr and file_hldr
        console_hldr.setFormatter(formatter)
        file_hldr.setFormatter(formatter)
        # add ch to logger
        self._logger.addHandler(console_hldr)
        self._logger.addHandler(file_hldr)

        return self._logger

    def clean(self):
        self._clean_store()
        self._clean_pdt()
        
    @abstractmethod
    def _clean_store(self):
        pass
    
    @abstractmethod
    def _clean_pdt(self):
        pass