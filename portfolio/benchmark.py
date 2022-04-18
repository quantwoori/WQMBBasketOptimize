from dbm.DBmssql import MSSQL
import pandas as pd

from datetime import datetime, timedelta
import settings.Sconstant as CONST
import warnings


class BenchMark:
    def __init__(self):
        # sort out DATE problem.
        self.TODAY, self.YSTDAY = self.clean_date()

        # Class local modules
        self.DB = MSSQL.instance()
        self.DB.login(id='wsol2', pw='wsol2')

    @staticmethod
    def clean_date() -> (datetime, datetime):
        dt0 = datetime.today()
        yst = dt0 - timedelta(days=1)
        # Monday - Friday event
        if yst.strftime('%w') == "0":
            yst = dt0 - timedelta(days=3)
            warn_msg = "Today is Monday. Changing yesterday to Friday"
            warnings.warn(warn_msg)
        return dt0, yst

    @staticmethod
    def __quantiwise_code_clean(value:str, prefix:str='A'):
        return value.replace(prefix, '')

    def get_weight(self, index_type:str, database:str='KRXDB', schema:str='', **kwargs):
        """
        :param index_type:
        :param kwargs:
            - 'date': "YYYYMMDD", str, designate search date manually
        :return:
        """
        if 'date' not in kwargs.keys():
            target_date = self.YSTDAY.strftime(CONST.QUANTIWISE_DFMT)
        else:
            target_date = kwargs['date']

        cnd = CONST.BENCHMARK_QRY.format(
            CONST.BENCHMARK_TABLE[index_type][0],
            CONST.BENCHMARK_TABLE[index_type][1],
            target_date
        )
        r = self.DB.select_db(
            database=database,
            schema=schema,
            table=CONST.BENCHMARK_TABLE[index_type][2],
            column=CONST.BENCHMARK_NCOL,
            condition=cnd
        )
        r = pd.DataFrame(r, columns=CONST.BENCHMARK_NCOL)

        # Make data usable
        r.CONSTITUENT_CODE = r.CONSTITUENT_CODE.apply(self.__quantiwise_code_clean)
        r.INDEX_WEIGHT = r.INDEX_WEIGHT.astype('float32')
        r.MARKET_CAP = r.MARKET_CAP.astype('float32')
        return r
