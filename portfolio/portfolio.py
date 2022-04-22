import settings.Sconstant as CONST

import scipy.optimize
import pandas as pd
import numpy as np

from typing import List, Iterable


class PortfolioOptimize:
    def __init__(self, benchmark:pd.DataFrame, factor_order:pd.DataFrame):
        self.data = self.process_data(
            benchmark=benchmark,
            score_order=factor_order,
            benchmark_ncol=benchmark.columns,
            ordering_ncol=factor_order,
            benchmark_key="CONSTITUENT_CODE",
            ordering_key="index_name"
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
        data.columns = ['stkcode', 'weight', 'fscore']

        # Add Column isin_order
        data['isin_order'] = np.sign(data['fscore'] + 1).fillna(0)
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
        return (self.data['fscore'].fillna() * -1).to_numpy().flatten().tolist()

    @property
    def boundary_const(self) -> [[float, float],]:
        result = list()
        for stk, w, score, ord in self.data.to_numpy():
            if bool(ord):
                # If weight != 0
                result.append(
                    [
                        max((w - CONST.STOCK_BOUNDARY), 0) / 100,  # weights cannot be negative
                        (w + CONST.STOCK_BOUNDARY) / 100
                    ]
                )
            else:
                # [0, 0] boundary.
                result.append([0, 0])
        return result

    def main(self):
        res = scipy.optimize.linprog(
            c=self.objective_const,
            A_eq=self.constraint_eq_left,
            b_eq=self.constraint_eq_right,
            bounds=self.boundary_const,
        )
        return res
