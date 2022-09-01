"""General functions
"""

from datetime import date, datetime, timedelta
from typing import Tuple, Union


def parse_date(dt: str) -> date:
    """parse string to date

    Args:
        dt (str): str

    Returns:
        date
    """
    try:
        return datetime.strptime(dt, "%Y-%m-%d").date()
    except:
        raise


def get_start_end_date(
    start: Union[str, date], end: Union[str, date]
) -> Tuple[date, date]:
    """Parse start date and end date strins to date

    If start date > end date it will change them, also
    max of end date will be yesterday

    Args:
        start (Union[str, date]): str "2022-01-01" or date format
        end (Union[str, date]): str "2022-01-01" or date format

    Raises:
        ValueError: start date can't be greater than yesterday

    Returns:
        Tuple[date, date]: (start_date, end_date)
    """
    dt_start = parse_date(start) if isinstance(start, str) else start
    yesterday = date.today() - timedelta(days=1)
    if dt_start > yesterday:
        raise ValueError("Start date can't be greater then yesterday")

    if end == "":
        dt_end = yesterday
    else:
        dt_end = parse_date(end) if isinstance(end, str) else end

    if dt_end > yesterday:
        dt_end = yesterday

    if dt_start > dt_end:
        dt_end, dt_start = dt_start, dt_end

    return dt_start, dt_end
