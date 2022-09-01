"""Validations classes
"""


class ScraperTypes:
    SCRAPY = "scrapy"
    REQUEST = "request"


class Scraper:
    """Get Scrapers configs"""

    SCRAPERS = {
        "refulog": {
            "config": {
                "url": "https://refu-log.com/",
                "type": ScraperTypes.SCRAPY,
            },
        },
        "growatt": {
            "config": {
                "url": "https://server.growatt.com/",
                "type": ScraperTypes.REQUEST,
            },
        },
    }

    def __init__(self, name):
        self.name = Scraper.get_scraper(name)
        self.dict_scraper = Scraper.SCRAPERS[name]
        self.config = self.dict_scraper["config"]
        self.type = self.config["type"]

    @staticmethod
    def get_scraper(name: str):
        """Check if Scraper name is in the list

        Args:
            name (str): scraper name

        Raises:
            ValueError: if scraper is not in the list

        Returns:
            _type_: scraper name
        """
        name = name.lower()
        dict_scraper = Scraper.SCRAPERS.get(name)
        if dict_scraper is None:
            raise ValueError("Invalid Scraper name")
        return name


class DataReturn:
    """Base to Dict that a spider returns"""

    LOGIN_STATUS = "login_status"
    DATA = "data"
    PLANT_INFO = "plant_info"

    def __init__(self):
        self.data_return = {
            DataReturn.LOGIN_STATUS: "NOK",
            DataReturn.DATA: [],
            DataReturn.PLANT_INFO: {},
        }

    def update(self, data: dict):
        key = list(data.keys())[0]
        field_data_return = self.data_return.get(key)
        if field_data_return is None or key == DataReturn.LOGIN_STATUS:
            self.data_return.update(data)

        if key == DataReturn.DATA:
            self.data_return[DataReturn.DATA].append(data)

        if key == DataReturn.PLANT_INFO:
            self.data_return[DataReturn.PLANT_INFO].update(data[DataReturn.PLANT_INFO])
