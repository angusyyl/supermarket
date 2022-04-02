import os

from pyspark.sql.types import StructType, StructField, StringType, FloatType, BooleanType
from pyspark.sql.functions import expr, col, substring, pandas_udf, regexp_extract
import pandas as pd

from .basecleaner import BaseCleaner
from config.appconfig import AppConfig


class CitySuperCleaner(BaseCleaner):
    price_patn_regex = '^\$(\d{1,3}+,)*+\d{1,3}+(\.\d\d){1}+$'
    
    def __init__(self):
        super().__init__('CITYSUPER', __name__)
        # override _pdt_schema in base class
        self._pdt_schema = StructType([
            StructField('s_desc', StringType(), True),
            StructField('price', StringType(), True),
            StructField('cat1', StringType(), True),
            StructField('img_url', StringType(), True),
            StructField('l_desc', StringType(), True),
            StructField('detail_url', StringType(), True),
            StructField('is_out_of_stock', BooleanType(), False),
            StructField('img', StringType(), True),
            StructField('scraped_ts', StringType(), True),
            StructField('cat2', StringType(), True),
            StructField('cat3', StringType(), True),
            StructField('pdt_id', StringType(), True),
        ])

    def _clean_store(self):
        store_raw_file = os.path.join(self._store_raw_data_dir, ''.join([self._supermarket.lower(), AppConfig.get_config('JSON_EXT', 'CONST')]))
        store_df = self.spark.read.json(store_raw_file, self._store_schema, multiLine=True)
        # store_df.printSchema()
        # store_df.show(10)
    
    @pandas_udf('string')
    def _price_wo_dollar(p:pd.Series) -> pd.Series:
        return p.str.slice(start=1).str.replace(',', '').astype('float64')
        
    def _clean_pdt(self):
        pdt_raw_file = os.path.join(self._pdt_raw_data_dir, ''.join([self._supermarket.lower(), AppConfig.get_config('JSON_EXT', 'CONST')]))
        pdt_df = self.spark.read.json(pdt_raw_file, self._pdt_schema, multiLine=True)
        pdt_df.printSchema()
        pdt_df.show(10)
        self._logger.info(f'Count of uncleaned products: {pdt_df.count()}.')
        cleaned_pdt_df = pdt_df.dropDuplicates(['s_desc', 'pdt_id', 'cat1', 'cat2', 'cat3'])
        cleaned_pdt_df = cleaned_pdt_df.select(regexp_extract(cleaned_pdt_df.price, type(self).price_patn_regex, 0).alias('price'))
        cleaned_pdt_df = cleaned_pdt_df.where(cleaned_pdt_df.price != '')
        cleaned_pdt_df = cleaned_pdt_df.select(type(self)._price_wo_dollar('price'))
        self._logger.info(f'Count of cleaned products: {cleaned_pdt_df.count()}.')
        cleaned_pdt_df.printSchema()
        cleaned_pdt_df.show(10)