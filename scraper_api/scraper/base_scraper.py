"""Base class to build the spiders
"""

import logging
from abc import ABC

from scraper_api.utils import get_start_end_date

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Basic class to create a spider"""

    name = "scraper_name"

    def __init__(
        self,
        user_login: str,
        password: str,
        start: str,
        end: str = "",
        debug=False,
        *args,
        **kwargs,
    ):
        """Base instance and variables to run a spiders

        Args:
            user_login (str): user login
            password (str): user password
            start (str): start date
            end (str, optional): end date. Defaults to "".
            debug (bool, optional): True for more verbose logs. Defaults to False.
        """
        super().__init__(*args, **kwargs)
        self.debug = bool(debug)

        self.user_login = user_login
        self.password = password
        self.dt_start, self.dt_end = get_start_end_date(start, end)

        logger.info(
            f"Starting Scraper: {self.user_login}, between {self.dt_start} -- {self.dt_end}"
        )
