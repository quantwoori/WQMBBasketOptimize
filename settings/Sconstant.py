# Global Constant for Optimizing Portfolio
# 바꿀 수 있는 곳 여기 하나!!
STOCK_BOUNDARY = 0.1  # in percent point
BIG_STOCKS, MID_STOCKS, SMALL_STOCKS = (30, 70, 100)  # 사이즈별 회사 개수

# 사이즈별 BOUNDARY
# 기존 Weight에 abs_low는 더하고, low는 곱함.
#    ->  max(w + abs_low, w * low) ~ min(w + abs_upp, w * upp)
#    ->  다음과 같이 weight 바운더리를 정한다.
#    ->  abs_low, abs_upp 는 %포인트
#    ->  upp, low는 %
BIG_BOUND = {
    "abs_low": -0.0020, "abs_upp": 0.0020,  # 대형주는 +- 20bp 절대값
    "low": 0.90, "upp": 1.10  # 대형주는 기존 weight의 +- 10%
}
MID_BOUND = {
    "abs_low": -0.0015, "abs_upp": 0.0015,  # 중형주는 +- 15bp 절대값
    "low": 0.85, "upp": 1.15  # 중형주는 기존 weight의 +- 15%
}
SML_BOUND = {
    "abs_low": -0.0010, "abs_upp": 0.0010,  # 소형주는 +- 10bp 절대값
    "low": 0.65, "upp": 1.35  # 소형주는 기존 weight의 +- 35%
}


# IMMUTABLE CONSTANT
# DO NOT CHANGE! # DO NOT CHANGE! # DO NOT CHANGE! # DO NOT CHANGE! # DO NOT CHANGE!
# Quantiwise table Configure
BENCHMARK_TABLE = {
    '코스피200': ['코스피 200', '코스피200', 'KOS200M_CONST_CLS'],
    '코스피지수': ['코스피 지수', '코스피지수', 'KOSPIM_CONST_CLS'],
    '코스닥150': ['코스닥 150', '코스닥150', 'KSQ150M_CONST_CLS'],
}
BENCHMARK_NCOL = ['CONSTITUENT_CODE', 'MARKET_CAP', 'INDEX_WEIGHT']
BENCHMARK_QRY = "(INDEX_NAME_KR = '{}' OR INDEX_NAME_KR = '{}') AND FILEDATE = '{}'"

# String Format Configure
QUANTIWISE_DFMT = '%Y%m%d'

# 지수에 소속된 주식 개수
BENCHMARK_STKS = {
    "코스피200": 200,
    "코스피지수": 600,
}

# DO NOT CHANGE! # DO NOT CHANGE! # DO NOT CHANGE! # DO NOT CHANGE! # DO NOT CHANGE!
# IMMUTABLE CONSTANT END