from portfolio.benchmark import BenchMark
import settings.Sconstant as CONST

from typing import Set


class Boundaries:
    def __init__(self, big_firms:int, middle_firms:int, small_firms:int, index_typ:str):
        # 만약 코스피 200 BM 이라면,
        # 대형주(big_firms) + 중형주(middle_firms) + 소형주(small_firms) 합이 200은 넘어야 함.
        assert (big_firms + middle_firms + small_firms) >= CONST.BENCHMARK_STKS[index_typ]

        # BM Weight 가져오기
        W = BenchMark().get_weight(index_type=index_typ)

        # 큰 것부터 작은 것 까지 정렬([:: -1]로 reverse sort)
        W = W.sort_values("MARKET_CAP")[:: -1]
        self.W = W.reset_index(drop=True)

        # FIRM NUMBERS
        self.BIG, self.MID, self.SMALL = big_firms, middle_firms, small_firms

    def sizewise_split(self) -> (Set, Set, Set):
        b = self.W[ : self.BIG]
        m = self.W[self.BIG : (self.BIG + self.MID)]
        s = self.W[(self.BIG + self.MID) : ]
        return (set(b['CONSTITUENT_CODE']),
                set(m['CONSTITUENT_CODE']),
                set(s['CONSTITUENT_CODE']))


if __name__ == "__main__":
    bound = Boundaries(30, 70, 100, index_typ="코스피200")
    b, m, s = bound.sizewise_split()
