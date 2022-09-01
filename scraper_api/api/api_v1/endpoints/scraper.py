"""Scraper's endpoints
"""


from fastapi import APIRouter
from scraper_api.api.schemas.schemas import ScraperData, ScraperResponse
from scraper_api.api.schemas.validations import apply_validations
from scraper_api.scraper.run import run

api_router = APIRouter()


@api_router.post("/scraper", response_model=ScraperResponse)
def scraper(data: ScraperData) -> dict:
    """Run the spider and return the data

    Args:
        data (ScraperData):

    Returns:
        dict: dict in the format of validations.DataReturn
    """
    data_dict = data.dict()
    data_dict = apply_validations(data_dict)
    scraper_data = run(
        data_dict["scraper_name"],
        user_login=data_dict["user_login"],
        password=data_dict["password"],
        start=data_dict["start_date"],
        end=data_dict["end_date"],
        debug=False,
    )

    return scraper_data
