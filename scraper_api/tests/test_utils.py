from datetime import date, timedelta

import pytest


@pytest.mark.parametrize(
    "start, end, output",
    [
        ("2022-01-01", "2022-01-30", (date(2022, 1, 1), date(2022, 1, 30))),
        ("2022-01-30", "2022-01-01", (date(2022, 1, 1), date(2022, 1, 30))),
        (
            "2022-01-01",
            "2050-01-01",
            (date(2022, 1, 1), date.today() - timedelta(days=1)),
        ),
    ],
)
def test_get_start_end_date(start, end, output):
    from scraper_api.utils import get_start_end_date

    func_return = get_start_end_date(start, end)
    assert output == func_return


@pytest.mark.parametrize("start, end", [("2050-01-01", "2022-01-30")])
def test_get_start_end_date_fail(start, end):
    from scraper_api.utils import get_start_end_date

    with pytest.raises(ValueError, match=r"Start date can't .*"):
        get_start_end_date(start, end)
