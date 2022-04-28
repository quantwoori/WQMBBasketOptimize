import settings.Sconstant as CONST

from portfolio.boundary import Boundaries

import scipy.optimize
import pandas as pd
import numpy as np

from typing import List, Iterable, Set


class PortfolioOptimize:
    def __init__(self, benchmark_name:str, benchmark:pd.DataFrame,
                 factor_order:pd.DataFrame, benchmark_key:str, order_key:str):
        self.BMNAME = benchmark_name

        self.data = self.process_data(
            benchmark=benchmark,
            score_order=factor_order,
            benchmark_ncol=benchmark.columns,
            ordering_ncol=factor_order.columns,
            benchmark_key=benchmark_key,
            ordering_key=order_key
        )

    @staticmethod
    def process_data(benchmark:pd.DataFrame, score_order:pd.DataFrame,
                     benchmark_ncol:Iterable, ordering_ncol:Iterable,
                     benchmark_key:str, ordering_key:str) -> pd.DataFrame:
        assert benchmark_key in benchmark_ncol, f"{benchmark_key} must be in benchmark_key"
        assert ordering_key in ordering_ncol, f"{ordering_key} must be in ordering_key"

        # Each DataFrame Segment
        benchmark_seg = benchmark[benchmark_ncol]
        ordering_seg = score_order[ordering_ncol]

        # Merge dataframe
        data = benchmark_seg.merge(
            ordering_seg,
            how='outer',
            right_on=ordering_key,
            left_on=benchmark_key
        )

        # Prefer certain segment
        col_seg1, col_seg2 = list(benchmark_ncol), list(ordering_ncol)
        col_seg2.remove(ordering_key)
        result_col = col_seg1 + col_seg2
        data = data[result_col]

        # Change name
        data.columns = ['stkcode', 'cap', 'weight', 'fscore']
        return data

    # constraint_eq_left and right:
    # equal weights. 1*w1 + 1*w2 + ... + 1*wn = 1 - epsilon
    @property
    def constraint_eq_left(self) -> [[float]]:
        return [[1.0] * len(self.data)]

    @property
    def constraint_eq_right(self) -> [float]:
        """
        0.99999 = 1 - epsilon
        such that epsilon is cash ratio
        """
        return [0.99999]

    @property
    def constraint_uneq_right(self) -> any:
        return None

    @property
    def objective_const(self) -> List:
        """
        sum of scores should be MINIMUM
        """
        return (self.data['fscore'].fillna(0) * -1).to_numpy().flatten().tolist()

    # BOUNDARY METHODS
    @staticmethod
    def __restraint(d:dict, nks:Iterable) -> bool:
        n = list()
        for i in nks:
            if i in d.keys():
                n.append(True)
            else:
                n.append(False)
        if len(n) > 0 and all(n):
            return True
        else:
            return False

    def __bound_wo_restrict(self) -> List:
        result = list()
        for stk, _, w, score in self.data.to_numpy():
            result.append(
                [
                    max((w - CONST.STOCK_BOUNDARY), 0) / 100,  # weights cannot be negative
                    (w + CONST.STOCK_BOUNDARY) / 100
                ]
            )
        return result

    def __bound_w_restrict(self, key:set) -> List:
        # SIZE WISE STOCK SPLIT
        bound = Boundaries(
            big_firms=CONST.BIG_STOCKS,
            middle_firms=CONST.MID_STOCKS,
            small_firms=CONST.SMALL_STOCKS,
            index_typ=self.BMNAME
        )
        b, m, s = bound.sizewise_split()

        result = list()
        for stk, _, w, score in self.data.to_numpy():
            # If in restriction <- add boundaries
            c = stk in key
            if c:
                if stk in b:
                    sizebound = CONST.BIG_BOUND
                elif stk in b:
                    sizebound = CONST.MID_BOUND
                else:
                    sizebound = CONST.SML_BOUND

                result.append(
                    [
                        max(
                            ((w / 100) + sizebound['abs_low']),
                            ((w / 100) * sizebound['low'])
                        ),
                        min(
                            ((w / 100) + sizebound['abs_upp']),
                            ((w / 100) * sizebound['upp'])
                        )
                    ]
                )

            # For stocks not in restrictions <- stick it to bm ratio
            else:
                result.append([w / 100, w / 100])
        return result

    def boundary_const(self, **kwargs) -> [[float, float],]:
        """
        :param kwargs: high, low

        restrictions meaning:
            restrictions limits the number of stocks that can be over or under weighted.
            If there is a restriction,
                cnd_yes_restriction will take you to __bound_w_restrict
            else:
                cnd_no_restriction will take you to __bound_wo_restrict
        """
        # Key Word Argument Check
        adjustable = None
        if self.__restraint(kwargs, ['adjust']):
            adjustable = kwargs['adjust']

        # If condition has restriction || If condition has no restriction
        cnd_no_restriction = adjustable is None

        if cnd_no_restriction:
            return self.__bound_wo_restrict()
        elif not cnd_no_restriction:
            return self.__bound_w_restrict(key=adjustable)
        else:
            raise RuntimeError("Both high and low restriction should be inserted")

    def main(self, **kwargs):
        cnd_high = "high" in kwargs.keys()
        cnd_low = "low" in kwargs.keys()
        if cnd_high and cnd_low:
            res = scipy.optimize.linprog(
                c=self.objective_const,
                A_eq=self.constraint_eq_left,
                b_eq=self.constraint_eq_right,
                bounds=self.boundary_const(adjust=kwargs['adjust']),
            )
        elif not cnd_high and not cnd_low:
            res = scipy.optimize.linprog(
                c=self.objective_const,
                A_eq=self.constraint_eq_left,
                b_eq=self.constraint_eq_right,
                bounds=self.boundary_const(),
            )
        else:
            raise RuntimeError("High must coexist with Low Restraint")
        return res

