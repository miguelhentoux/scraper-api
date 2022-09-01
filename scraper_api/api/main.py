"""Main App to run the API
"""

from fastapi import APIRouter, FastAPI
from scraper_api.api.api_v1 import api as v1
from scraper_api.api.core.config import api_settings

app = FastAPI(title="Scraper API")

main_router = APIRouter()


@main_router.get("/")
def root():
    """Just a testing home page"""
    return {"message": "Olar"}


app.include_router(v1.api_router, prefix=api_settings.API_V1_STR)
app.include_router(main_router)
