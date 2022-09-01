"""Base class to create scrapy spiders
"""

from scraper_api.scraper.base_scraper import BaseScraper
from scrapy import Spider


class BaseSpider(BaseScraper, Spider):
    """Base class to create scrapy spiders"""

    allowed_domains = [""]
    start_urls = [""]

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        Spider.__init__(self, *args, **kwargs)
        BaseScraper.__init__(self, *args, **kwargs)
