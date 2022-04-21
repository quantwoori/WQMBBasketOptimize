from dbm.DBquant import PyQuantiwise
from dbm.DBmssql import MSSQL

from typing import Iterable


class Earnings:
    def __init__(self):
        # class local modules
        self.server = MSSQL.instance()
        self.qt = PyQuantiwise()

    def revision_ratio(self, universe:Iterable):

        ...

    def eps_delta(self):
        """
        연간 EPS 비교
        (t달 - t-1달) / t-1달
        """
        ...

    def earnings_dela(self):
        """

        :return:
        """

    def get_factors(self):
        ...


if __name__ == "__main__":
    e = Earnings()
    r = e.qt.css_data_multi(
        stock_code_ls=['005930', '000270'],
        start_date='20220401',
        end_date='20220422',
        item='EPS',
        concensus_period='연결누적',
    )

    r2 = e.qt.css_data_multi(
        stock_code_ls=['005930', '000270'],
        start_date='20220401',
        end_date='20220422',
        item='영업이익',
        concensus_period='연결순액',
    )
