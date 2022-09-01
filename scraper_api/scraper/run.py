""" Calleble to run the scrapers
"""

import argparse
import logging
import sys

# fmt: off
sys.path.append('.') # fix problem with PyPath to run localy
# fmt: on

from scraper_api.scraper.request_scraper.run import run_request
from scraper_api.scraper.solar_scraper.run import run_scrapy
from scraper_api.settings import settings
from scraper_api.utils import get_start_end_date
from scraper_api.validations import Scraper, ScraperTypes

log = logging.getLogger(__name__)


def run(scraper_name: str, **kwargs) -> dict:
    """Function to run the scrapers

    Scrapers can by of two types:
    SCRAPY: will run inside of scrapy, fetching data from the website
    REQUESTS: the website has already an API to fetch the data

    Args:
        scraper_name (str): scraper name
        kwargs: Spider's args
    Returns:
        dict: return dict as model in validations.DataReturn
    """
    scraper = Scraper(scraper_name)
    data_return = {}
    if scraper.type == ScraperTypes.SCRAPY:
        data_return = run_scrapy(scraper_name, **kwargs)
    if scraper.type == ScraperTypes.REQUEST:
        data_return = run_request(scraper_name, **kwargs)

    if kwargs.get("debug"):
        log.info(data_return)
    return data_return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run solar scrapers.")
    parser.add_argument(
        "-n",
        "--scraper_name",
        required=True,
        help="Scraper name",
        type=Scraper.get_scraper,
    )
    parser.add_argument(
        "-l", "--user_login", required=True, help="User to login in the website"
    )
    parser.add_argument(
        "-p", "--password", required=True, help="Password to login in the website"
    )
    parser.add_argument("-s", "--start", required=True, help="Start date. Format Y-m-d")
    parser.add_argument(
        "-e",
        "--end",
        required=False,
        help="End date. Default value = yesterday. Format Y-m-d",
        default="",
    )
    parser.add_argument(
        "--debug",
        action=argparse.BooleanOptionalAction,
        help="Enable DEBUG mode, change log level to DEBUG and open browser",
    )

    args = parser.parse_args()

    get_start_end_date(args.start, args.end)

    log.info(
        f"Executing {args.scraper_name} - {args.user_login} from '{args.start}' until ''."
    )

    user_login, password = args.user_login, args.password
    if settings.ENV == "dev" and not bool(args.user_login):
        user_login = settings.DEV_KEYS[args.scraper_name]["user_login"]
        password = settings.DEV_KEYS[args.scraper_name]["password"]

    assert user_login
    run(
        args.scraper_name,
        user_login=user_login,
        password=password,
        start=args.start,
        end=args.end,
        debug=args.debug,
    )
