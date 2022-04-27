from factor.Ufunc import neighboring_elements, get_universe
from factor.Udate import BackTestDates

from dbm.DBquant import PyQuantiwise
from dbm.DBmssql import MSSQL

import pandas as pd

from typing import Iterable, Dict
from datetime import datetime


class Earnings:
    MD = {
        1: ('{}0101', '{}0131'),
        2: ('{}0201', '{}0229'),
        3: ('{}0301', '{}0331'),
        4: ('{}0401', '{}0430'),
        5: ('{}0501', '{}0531'),
        6: ('{}0601', '{}0630'),
        7: ('{}0701', '{}0731'),
        8: ('{}0801', '{}0831'),
        9: ('{}0901', '{}0930'),
        10: ('{}1001', '{}1031'),
        11: ('{}1101', '{}1130'),
        12: ('{}1201', '{}1231'),
    }
    MDD = {
        1: ['{}12', -1], 2: ['{}03', 0], 3: ['{}03', 0],
        4: ['{}03', 0], 5: ['{}06', 0], 6: ['{}06', 0],
        7: ['{}06', 0], 8: ['{}09', 0], 9: ['{}09', 0],
        10: ['{}09', 0], 11: ['{}12', 0], 12: ['{}12', 0],
    }

    def __init__(self, universe:str, time_start:datetime, time_end:datetime):
        # class local modules
        self.server = MSSQL.instance()
        self.qt = PyQuantiwise()

        # class constant
        self.U = universe
        self.T0, self.T1 = time_start, time_end

    def revision_ratio(self, universe:Iterable):
        """
        Revision ratio is not recorded in database
        """
        raise NotImplementedError

    @staticmethod
    def target_yymm(year):
        return f"{year}12"

    def eps_val(self, univ:Iterable, year:int, month:int) -> pd.DataFrame:
        """
        연간 EPS 비교  -  연결 누적
        (t달 - t-1달) / t-1달
        """
        r = self.qt.css_data_multi(
            stock_code_ls=univ,
            start_date=self.MD[month][0].format(year),
            end_date=self.MD[month][1].format(year),
            item='EPS',
            consensus_period='연결누적'
        )
        r.VAL = r.VAL.astype('float32')

        r = r[r.YYMM == self.target_yymm(year)]
        r = r.pivot_table(values='VAL', columns='CMP_CD', index='CNS_DT')
        return r

    @staticmethod
    def _eps_delta_calc(before_df:pd.DataFrame, after_df:pd.DataFrame) -> pd.DataFrame:
        w = pd.concat([before_df, after_df])
        w = w.ffill()
        wpct = w.pct_change()[1:]
        return wpct

    def eps_delta(self, universe:str, period_start:datetime, period_end:datetime) -> [pd.DataFrame]:
        """
        self.eps_val() 에서 받은 자료를 이용
        date 는 Udate의 BackTestDate 이용 -> Ufunc.neighboring_elements으로 해결
        """
        print("[WQMB] >>> GETTING EPS DELTA FACTOR")
        btd = BackTestDates()
        dates = btd.generate_dates(period_start, period_end)

        result = list()
        for y, m in dates:
            u = get_universe(y, m, universe)
            r = self.eps_val(
                univ=u,
                year=y,
                month=m
            )
            result.append(r[:1])

        result = neighboring_elements(result)

        return list(map(
            lambda x: self._eps_delta_calc(x[0], x[1]),
            result)
        )

    def earnings_val(self, univ:Iterable, year:int, month:int) -> (pd.DataFrame, str):
        """
        분기별로 매칭 비교

        1분기: (1, 2, 3)
        2분기: (4, 5, 6)
        3분기: (7, 8, 9)
        4분기: (10, 11, 12)

        (t달 - t-1달) / t-1달
        :return:
        """
        r = self.qt.css_data_multi(
            stock_code_ls=univ,
            start_date=self.MD[month][0].format(year),
            end_date=self.MD[month][1].format(year),
            item='영업이익',
            consensus_period='연결순액'
        )
        r.VAL = r.VAL.astype('float32')
        r = r.loc[r["CNS_DT"] == r["CNS_DT"].min()]
        return r.pivot_table(values="VAL", index="CMP_CD", columns="YYMM"), r["CNS_DT"].min()

    @staticmethod
    def __earnings_delta_calc(before_df:pd.DataFrame, after_df:pd.DataFrame, date:str) -> pd.DataFrame:
        result = list()
        col = ['date', 'stk', 'val']
        for stk in after_df.index:
            # Stock-code wise before, after segmentation
            before_seg = before_df.loc[before_df.index == stk]
            after_seg = after_df.loc[after_df.index == stk]
            seg = pd.concat([before_seg, after_seg]).dropna(axis=1)

            if not seg.empty and (len(seg) >= 2):
                val = seg.pct_change()[1:].to_numpy()[0][0]
                result.append([date, stk, val])
            else:
                result.append([date, stk, 0.0])
        result = pd.DataFrame(result, columns=col)
        return result.pivot_table(values="val", index="date", columns="stk")

    def earnings_delta(self, universe:str, period_start:datetime, period_end:datetime):
        """
        self.earnings_val() 에서 받은 자료를 이용
        date 는 Udate의 BackTestDate 이용 -> Ufunc.neighboring_elements로 해결
        """
        print("[WQMB] >>> GETTING EARNINGS DELTA FACTOR")
        btd = BackTestDates()
        dates = btd.generate_dates(period_start, period_end)

        result, date = list(), list()
        for y, m in dates:
            u = get_universe(y, m, universe)
            r, d = self.earnings_val(
                univ=u,
                year=y,
                month=m
            )
            result.append(r)
            date.append(d)

        result = neighboring_elements(result)
        date = date[1:]

        return list(map(
            lambda x: self.__earnings_delta_calc(x[0][0], x[0][1], x[1]),
            zip(result, date)
        ))

    def filters_val(self, univ:Iterable, year:int, month:int):
        r = self.qt.css_data_multi(
            stock_code_ls=univ,
            start_date=self.MD[month][0].format(year),
            end_date=self.MD[month][1].format(year),
            item='EPS참여증권사',
            consensus_period='연결순액'
        )
        r.VAL = r.VAL.astype('int32')

        r = r[r.YYMM == self.target_yymm(year)]
        r = r.pivot_table(values='VAL', columns='CMP_CD', index='CNS_DT')
        return r

    def filters(self, universe:str, period_start:datetime, period_end:datetime, thres:int=3) -> Dict:
        btd = BackTestDates()
        dates = btd.generate_dates(period_start, period_end)

        result = dict()
        for y, m in dates:
            u = get_universe(y, m, universe)
            r = self.filters_val(
                univ=u,
                year=y,
                month=m
            )
            result[r[:1].index[0]] = {
                k for k, v in zip(r[:1].columns, r[:1].to_numpy()[0])
                if v > thres
            }  # Pick Consensus Count More than 5(thres)

        return result

    @staticmethod
    def __calc_factor_scores(factor1:pd.DataFrame, factor2:pd.DataFrame) -> (pd.Series, str):
        f1, f2 = factor1.transpose().dropna(), factor2.transpose().dropna()

        # Normalize
        f1 = (f1 - f1.mean()).div(f1.std())
        f2 = (f2 - f2.mean()).div(f2.std())
        return (f1[f1.columns[0]] + f2[f2.columns[0]]).sort_values(), f1.columns[0]

    def get_factors(self, active_weight:int) -> Dict:
        # Filters. Consensus Count <= thres will be eliminated
        fil = self.filters(self.U, self.T0, self.T1)

        # EPS DELTA
        f0 = self.eps_delta(self.U, self.T0, self.T1)
        f01 = list(map(lambda x: x[[s for s in fil[x.index[0]]]], f0))

        # Earnings DELTA
        f1 = self.earnings_delta(self.U, self.T0, self.T1)
        f11 = list(map(lambda x: x[[s for s in fil[x.index[0]]]], f1))

        print("[WQMB] >>> OVERWEIGHT UNDERWEIGHT DIST.")
        ap = dict()
        for fac0, fac1 in zip(f01, f11):
            factor_score, date = self.__calc_factor_scores(fac0, fac1)
            ap[date] = dict()
            if len(factor_score) >= active_weight * 2:
                ap[date]['o'] = set(factor_score.index[(-1 * active_weight):])
                ap[date]['u'] = set(factor_score.index[:active_weight])
                ap[date]['fs'] = factor_score
            else:
                print("fucking analysts slacked off", date, len(factor_score))
                continue
        return ap


if __name__ == "__main__":
    # Setup
    T1, T2 = (
        datetime(2020, 2, 1),
        datetime.today()
    )
    U = 'ks200'

    e = Earnings(U, T1, T2)
    sc = e.get_factors(active_weight=10)
    # '20220401'


