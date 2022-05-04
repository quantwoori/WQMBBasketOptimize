from dbm.DBmssql import MSSQL
from dbm.DBquant import PyQuantiwise


class SubjectTo:
    def __init__(self):
        # Class Modules
        self.server = MSSQL.instance()
        self.qt = PyQuantiwise()

    def classification(self):
        ...

    def market_capital(self):
        ...
