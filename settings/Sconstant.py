# Global Constant for Optimizing Portfolio
STOCK_BOUNDARY = 0.1  # in percent point


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