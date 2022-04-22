from dbm.DBmssql import MSSQL
from typing import Iterable


def neighboring_elements(ls:Iterable):
    l = len(ls)
    res = list()
    for i in range(1, l):
        res.append(
            (ls[i - 1], ls[i])
        )
    return res


def get_universe(year:int, month:int, index_name:str):
    server = MSSQL.instance()

    cnd = [
        f"year = {year}",
        f"chg_no = {month}",
        f"ind_ = '{index_name}'"
    ]
    col = server.get_columns(
        database="WSOL",
        schema="dbo",
        table_name="indcomp"
    )
    u = server.select_db(
        database="WSOL",
        schema="dbo",
        table="indcomp",
        column=col,
        condition=" and ".join(cnd)
    )
    return [e[3] for e in u]
