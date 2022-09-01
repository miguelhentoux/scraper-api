"""Run spiders in scrapy to fetch data from the website
"""

import logging
import os

import crochet
from scraper_api.validations import DataReturn
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

log = logging.getLogger(__name__)
crochet.setup()
from typing import Callable


@crochet.wait_for(timeout=60)
def _run_inside_crochet(add_item: Callable, scraper_name: str, **kargs):
    """Scrapy has to be run inside of crochet to not break
    the  Twisted kernel from FAST API

    Args:
        add_item (Callable): function to add itens in the data_return
        scraper_name (str): scraper name
        kargs: spider's args

    Returns:
        _type_: Deferred object
    """
    os.environ["SCRAPY_SETTINGS_MODULE"] = "scraper_api.scraper.solar_scraper.settings"
    scraper_settings = get_project_settings()
    if kargs.get("debug"):
        configure_logging({"LOG_LEVEL": "DEBUG"})
        scraper_settings["LOG_LEVEL"] = "DEBUG"
    else:
        configure_logging()

    runner = CrawlerRunner(scraper_settings)
    crawler = runner.create_crawler(scraper_name)
    crawler.signals.connect(add_item, signal=signals.item_passed)
    d = crawler.crawl(**kargs)
    return d


def run_scrapy(scraper_name: str, **kargs) -> dict:
    """Run with scrapy

    Args:
        scraper_name (str): scraper name
        kargs: spider's args
    Returns:
        dict: dict return as DataReturn model
    """
    data_return = DataReturn()

    def add_item(item: dict, *args, **kwargs):
        assert len(item) == 1, "Item must have just one item"
        data_return.update(item)

    _run_inside_crochet(add_item, scraper_name, **kargs)

    return data_return.data_return
