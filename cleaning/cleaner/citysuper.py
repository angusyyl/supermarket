import os
import re
from functools import reduce

from pyspark.sql.types import StructType, StructField, StringType, FloatType, BooleanType
from pyspark.sql.functions import expr, col, substring, pandas_udf, regexp_extract, regexp_replace, trim
from pyspark.sql import DataFrame
import pandas as pd

from .basecleaner import BaseCleaner
from config.appconfig import AppConfig


class CitySuperCleaner(BaseCleaner):
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
        self.PRICE_PATN_REGEX = '^\$(\d{1,3},)*+\d{1,3}(\.\d\d){1}$'
        self.MEASUREMENT_REGEX = '\((\d+|\d+ x \d+)(g|kg|mL|L|pack|packs|pc|pcs)\)$'
        self.QUANTITY_REGEX = r'\d+|\d+ x \d+'
        self.UNIT_REGEX = r'(g|kg|mL|L|pack|packs|pc|pcs)$'

    def _clean_store(self):
        store_raw_file = os.path.join(self._store_raw_data_dir, ''.join(
            [self._supermarket.lower(), AppConfig.get_config('JSON_EXT', 'CONST')]))
        store_df = self.spark.read.json(
            store_raw_file, self._store_schema, multiLine=True)
        # store_df.printSchema()
        # store_df.show(10)

    @pandas_udf('string')
    def _price_wo_dollar(p: pd.Series) -> pd.Series:
        return p.str.slice(start=1).str.replace(',', '')

    def _clean_pdt(self):
        pdt_raw_files = [f for f in os.listdir(
            self._pdt_raw_data_dir) if f.startswith(self._supermarket.lower())]
        dfs = []
        for f in pdt_raw_files:
            dfs.append(self.spark.read.json(os.path.join(
                self._pdt_raw_data_dir, f), self._pdt_schema, multiLine=True))
        df = reduce(DataFrame.union, dfs)

        self._logger.info(f'Count of uncleaned products: {df.count()}.')

        df = df.dropDuplicates(['s_desc', 'pdt_id', 'cat1', 'cat2', 'cat3'])
        # remove empty price
        df = df.filter(df.price.isNotNull())
        # remove any rows not in price format
        df = df.filter(regexp_extract(
            col('price'), self.PRICE_PATN_REGEX, 0) != '')
        # format price to numeric
        df = df.withColumn('price', type(
            self)._price_wo_dollar('price').astype('float'))
        # remove any rows which are out of stock
        df = df.filter(df.is_out_of_stock == False)
        # remove any rows having no short description or 1st category
        df = df.filter(df.s_desc.isNotNull() & df.cat1.isNotNull())
        # trim s_desc, cat1, cat2, cat3 columns
        df = df.withColumn('s_desc', trim(regexp_replace('s_desc', u'\u00a0', '')))
        df = df.withColumn('cat1', trim(regexp_replace('cat1', u'\u00a0', '')))
        df = df.withColumn('cat2', trim(regexp_replace('cat2', u'\u00a0', '')))
        df = df.withColumn('cat3', trim(regexp_replace('cat3', u'\u00a0', '')))
        # add measurement column
        df = df.withColumn('measurement', regexp_replace(regexp_extract(
            col('s_desc'), self.MEASUREMENT_REGEX, 0), r'(^\(|\)$)', ''))
        # add quantity column
        df = df.withColumn('qny', regexp_extract(
            col('measurement'), self.QUANTITY_REGEX, 0))
        # add unit column
        df = df.withColumn('unit', regexp_extract(
            col('measurement'), self.UNIT_REGEX, 0))
        self._logger.info(f'Count of cleaned products: {df.count()}.')
        # df.printSchema()
        df.show(10)

        df.createOrReplaceTempView('citysuper_products')
        # BBQ theme
        bbq_df = (self.spark.sql('SELECT s_desc, price, qny, unit, cat1, cat2, cat3 \
                                    FROM citysuper_products \
                                    WHERE \
                                    (cat1 = "肉類" AND (s_desc LIKE "%燒肉%" OR s_desc LIKE "%燒烤%")) \
                                    OR \
                                        (cat1 = "乾貨區" AND cat2 = "調味料及烹調配料" AND (s_desc LIKE "%燒肉%" OR s_desc LIKE "%燒烤%")) \
                                    OR \
                                        (cat2 = "蔬菜" \
                                            AND (s_desc LIKE "%蘆筍%" \
                                                OR s_desc LIKE "%番薯%" \
                                                OR s_desc LIKE "%焗薯%" \
                                                OR s_desc LIKE "%粟米%" \
                                                OR s_desc LIKE "%茄子%" \
                                                OR s_desc LIKE "%南瓜%" \
                                                OR s_desc LIKE "%韮菜%" \
                                                OR s_desc LIKE "%燈籠椒%" \
                                                OR s_desc LIKE "%蒜頭%")) \
                                    OR \
                                        cat3 = "蘑菇" \
                                '))
        bbq_df_cnt = bbq_df.count()
        bbq_df.show(bbq_df_cnt, truncate=False)
        self._logger.info(f'{bbq_df_cnt} products of BBQ theme.')

        # Hot pot theme
        hotpot_df = (self.spark.sql('SELECT s_desc, price, qny, unit, cat1, cat2, cat3 \
                                        FROM citysuper_products \
                                        WHERE cat1 = "肉類" \
                                        AND s_desc LIKE "%火鍋%"'))
        hotpot_df_cnt = hotpot_df.count()
        hotpot_df.show(hotpot_df_cnt, truncate=False)
        self._logger.info(f'{hotpot_df_cnt} products of hotpot theme.')

        # Home movie theme
        # home_movie_df
        
        # BBQ + Hot pot themes
        # union_df = (self.spark.sql(' \
        #                         SELECT "BBQ", s_desc, price, qny, unit, cat1, cat2, cat3 \
        #                             FROM citysuper_products \
        #                             WHERE \
        #                             (cat1 = "肉類" AND (s_desc LIKE "%燒肉%" OR s_desc LIKE "%燒烤%")) \
        #                             OR \
        #                                 (cat2 = "調味料及烹調配料" AND (s_desc LIKE "%燒肉%" OR s_desc LIKE "%燒烤%")) \
        #                             OR \
        #                                 (cat2 = "蔬菜" \
        #                                     AND (s_desc LIKE "%蘆筍%" \
        #                                         OR s_desc LIKE "%番薯%" \
        #                                         OR s_desc LIKE "%焗薯%" \
        #                                         OR s_desc LIKE "%粟米%" \
        #                                         OR s_desc LIKE "%茄子%" \
        #                                         OR s_desc LIKE "%南瓜%" \
        #                                         OR s_desc LIKE "%韮菜%" \
        #                                         OR s_desc LIKE "%燈籠椒%" \
        #                                         OR s_desc LIKE "%蒜頭%")) \
        #                             OR \
        #                                 cat3 = "蘑菇" \
        #                         UNION \
        #                         SELECT "HOTPOT", s_desc, price, qny, unit, cat1, cat2, cat3 \
        #                             FROM citysuper_products \
        #                             WHERE cat1 = "肉類" \
        #                             AND s_desc LIKE "%火鍋%" \
        #                         '))
        # union_df.show(union_df.count(), truncate=False)