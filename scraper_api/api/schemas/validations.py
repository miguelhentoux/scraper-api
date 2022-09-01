"""Request validation functions
Add the @valid_method decorator to add the method to the list the will be run
"""

from fastapi import HTTPException
from scraper_api.utils import get_start_end_date
from scraper_api.validations import Scraper

VALIDATIONS_METHODS = []


def valid_method(func, *args, **kwargs):
    """Decorator to add methos into the list"""
    VALIDATIONS_METHODS.append(func)


@valid_method
def __valid_date(data_dict: dict) -> dict:
    """Valid request payload data"""
    try:
        data_dict["start_date"], data_dict["end_date"] = get_start_end_date(
            data_dict["start_date"], data_dict["end_date"]
        )

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return data_dict


@valid_method
def __valid_scraper_name(data_dict: dict) -> dict:
    """Valid request payload scraper name"""
    try:
        data_dict["scraper_name"] = Scraper.get_scraper(data_dict["scraper_name"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return data_dict


def apply_validations(data_dict: dict) -> dict:
    """Run all validation in the list"""
    for method in VALIDATIONS_METHODS:
        data_dict = method(data_dict)
    return data_dict
