"""Requests/Responses schemas
"""

from datetime import date, timedelta

from pydantic import BaseModel
from scraper_api.validations import DataReturn


class ScraperData(BaseModel):
    """Scraper request model
    """
    scraper_name: str
    user_login: str
    password: str
    start_date: date
    end_date: date = date.today() - timedelta(days=1)


class ScraperResponse(BaseModel):
    """Scraper response model
    """
    locals()[DataReturn.LOGIN_STATUS] = "NOK"
    locals()[DataReturn.DATA] = [{"2022-01-01": 20.4}, {"2022-01-01": 20.4}]
    locals()[DataReturn.PLANT_INFO] = {}
