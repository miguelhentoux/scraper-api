"""Run spiders that already have an API with requests
"""

import logging
import pkgutil
import traceback

from scraper_api.scraper.request_scraper import spiders

log = logging.getLogger(__name__)


def get_instance(scraper_name: str):
    """Get the spider instance

    Args:
        scraper_name (str): scraper name

    Returns:
        _type_: Spider class
    """
    list_modules = [modname for _, modname, _ in pkgutil.iter_modules(spiders.__path__)]
    list_modules.remove("base_spider")
    assert scraper_name in list_modules, f"Scraper ({scraper_name}) not in modules"

    mod = __import__(
        f"{spiders.__name__}.{scraper_name}", fromlist=[scraper_name.capitalize()]
    )
    return getattr(mod, scraper_name.capitalize())


def run_request(scraper_name: str, **kargs) -> dict:
    """Run spider from requests

    Args:
        scraper_name (str): scraper name
        kargs: spider's args
    Returns:
        dict: dict in validations.DataReturn format
    """
    instance = get_instance(scraper_name)
    scraper = instance(**kargs)
    try:
        # Every spiders needs a run function
        scraper.run()
    except:
        traceback.print_exc()

    # Every spiders needs a return_data function
    return scraper.return_data()
