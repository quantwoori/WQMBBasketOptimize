from portfolio.portfolio import PortfolioOptimize
from portfolio.benchmark import BenchMark
from factor.Fearn import Earnings

import pandas as pd

from datetime import datetime


# Container Method
def container_benchmark(weight: pd.DataFrame) -> (pd.DataFrame, str):  # Data, key
    return weight, "CONSTITUENT_CODE"


def container_factor(factor: pd.Series) -> (pd.DataFrame, str):  # Data, key
    f = pd.DataFrame(factor)

    f = f.reset_index()
    f.columns = ["Stocks", "Score"]
    return f, "Stocks"


# Benchmark
bm = BenchMark()
bw = bm.get_weight(index_type='코스피200')

# Factors
# first keys are [dates, ]  ex) '20220401'
# second keys are 'o'  'u'  'fs', for overweight, underweight, and factor score
T1, T2 = (
    datetime(2022, 1, 1),
    datetime.today()
)
U = 'ks200'
e = Earnings(U, T1, T2)
sc = e.get_factors(active_weight=10)


# Portfolio
b, bk = container_benchmark(bw)
o, ok = container_factor(sc['20220401']['fs'])

p = PortfolioOptimize("코스피200", b, o, bk, ok)
r = p.main(adjust=sc['20220401']['keys'])

# Report
ss = pd.DataFrame(r.x)
ss.index = bw['CONSTITUENT_CODE'].apply(lambda x: f"A{x}")

bw['CONSTITUENT_CODE'] = bw['CONSTITUENT_CODE'].apply(lambda x: f"A{x}")
rpt = pd.concat([ss, bw.set_index('CONSTITUENT_CODE')], axis=1)
rpt['INDEX_WEIGHT'] = rpt['INDEX_WEIGHT'] / 100
rpt.columns = ["AP", "_", "BM"]
rpt["AP - BM"] = rpt["AP"] - rpt["BM"]
rpt = rpt[["AP", "BM", "AP - BM"]]

rpt.to_csv("result.csv")