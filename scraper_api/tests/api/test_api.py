import json

import pytest
import requests
from scraper_api.validations import Scraper

URL_BASE = "http://127.0.0.1:8000"


def test_api_running():
    response = requests.get(URL_BASE)
    response.raise_for_status()


@pytest.mark.parametrize("scraper_name", [name for name in Scraper.SCRAPERS.keys()])
def test_api_scraper(scraper_name):
    endpoint = URL_BASE + "/api/v1/recipes/scraper"
    from scraper_api.settings import settings
    from scraper_api.validations import DataReturn

    user_login = settings.DEV_KEYS[scraper_name]["user_login"]
    password = settings.DEV_KEYS[scraper_name]["password"]
    payload = {
        "scraper_name": scraper_name,
        "user_login": user_login,
        "password": password,
        "start_date": "2021-01-01",
        "start_date": "2021-01-30",
    }

    headers = {"Content-Type": "application/json"}

    response = requests.request(
        "POST", endpoint, headers=headers, data=json.dumps(payload)
    )
    response.raise_for_status()
    data_return = json.loads(response.text)
    assert data_return[DataReturn.LOGIN_STATUS] == "OK"
    assert len(data_return[DataReturn.DATA])
    assert data_return[DataReturn.PLANT_INFO]
