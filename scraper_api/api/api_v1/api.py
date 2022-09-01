"""Router to v1
"""

from fastapi import APIRouter
from scraper_api.api.api_v1.endpoints import scraper

api_router = APIRouter()
api_router.include_router(scraper.api_router, prefix="/recipes", tags=["recipes"])
