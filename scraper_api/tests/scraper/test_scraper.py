import pytest
from scraper_api.validations import Scraper


@pytest.mark.parametrize("scraper_name", [name for name in Scraper.SCRAPERS.keys()])
def test_scraper(scraper_name):
    from scraper_api.scraper.run import run
    from scraper_api.settings import settings
    from scraper_api.validations import DataReturn

    user_login = settings.DEV_KEYS[scraper_name]["user_login"]
    password = settings.DEV_KEYS[scraper_name]["password"]

    data_return = run(
        scraper_name,
        user_login=user_login,
        password=password,
        start="2021-01-01",
        end="2021-01-31",
    )

    assert data_return[DataReturn.LOGIN_STATUS] == "OK"
    assert len(data_return[DataReturn.DATA])
    assert data_return[DataReturn.PLANT_INFO]
