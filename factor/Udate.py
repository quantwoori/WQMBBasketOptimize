from datetime import datetime
from dateutil.relativedelta import relativedelta
from factor.Ufunc import neighboring_elements


class BackTestDates:
    """
    Returns backtest pairs
    [((2022, 1), (2022, 2)),
     ((2022, 2), (2022, 3)),
     ((2022, 3), (2022, 4)),]
    """
    @staticmethod
    def generate_dates(start_date:datetime, end_date:datetime):
        assert end_date >= start_date

        result = list()
        mov = start_date
        while mov <= end_date:
            result.append(
                (mov.year, mov.month)
            )
            mov += relativedelta(months=1)

        return result


if __name__ == "__main__":
    btd = BackTestDates()
    t1, t2 = (
        datetime(2020, 2, 1),
        datetime.today()
    )
    r1 = btd.generate_dates(t1, t2)
    r2 = neighboring_elements(r1)
