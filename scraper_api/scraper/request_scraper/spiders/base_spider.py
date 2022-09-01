"""Base class to create Requests Spiders
"""

import logging

from scraper_api.scraper.base_scraper import BaseScraper
from scraper_api.validations import DataReturn


class BaseSpider(BaseScraper):
    allowed_domains = [""]
    start_urls = [""]

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        BaseScraper.__init__(self, *args, **kwargs)
        self.data_return = DataReturn()
        self.status_login = "NOK"
        self.plant_info = {}
        if self.debug:
            logging.basicConfig(level=logging.INFO)
        else:
            logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

    def run(self):
        # Every spiders needs a run function
        assert False, "Run not implemented"

    def return_data(self):
        return self.data_return.data_return
