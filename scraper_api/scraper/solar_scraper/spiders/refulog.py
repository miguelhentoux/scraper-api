"""Spider to scraper refu-log.com
"""

import json
from datetime import date, timedelta

import scrapy
from scraper_api.scraper.solar_scraper.spiders.base_spider import BaseSpider
from scraper_api.validations import DataReturn
from scrapy.http import FormRequest
from scrapy.utils.response import open_in_browser


class RefulogSpider(BaseSpider):
    """refu-log.com Spider"""

    name = "refulog"
    allowed_domains = ["refu-log.com"]
    start_urls = ["http://refu-log.com/"]

    def parse(self, response):
        """First function"""
        yield scrapy.Request("https://refu-log.com/", self.parse_login)

    def parse_login(self, response):
        """Send login forms as a request

        Args:
            response (_type_)
        """
        view_state = response.xpath("//*[@id='__VIEWSTATE']").attrib["value"]
        generator = response.xpath("//*[@id='__VIEWSTATEGENERATOR']").attrib["value"]
        event_validation = response.xpath("//*[@id='__EVENTVALIDATION']").attrib[
            "value"
        ]
        formdata = {
            "__VIEWSTATE": view_state,
            "__VIEWSTATEGENERATOR": generator,
            "__EVENTVALIDATION": event_validation,
            "ctl00$headerControl$loginControl$txtUsername": f"{self.user_login}",
            "ctl00$headerControl$loginControl$txtPassword": f"{self.password}",
            "ctl00$headerControl$loginControl$btnLogin": "Anmelden",
        }

        yield FormRequest.from_response(
            response,
            formdata=formdata,
            callback=self.parse_after_login_to_dashboard,
            meta={
                "handle_httpstatus_list": [302],
            },
        )

    def parse_after_login_to_dashboard(self, response):
        """After login redirect to the dashboard page"""
        self.logger.info("after login")
        yield scrapy.Request(
            "https://refu-log.com/Dashboard.aspx",
            callback=self.parse_after_login_get_headers,
            meta={
                "handle_httpstatus_list": [302],
            },
        )

    def parse_after_login_get_headers(self, response):
        """Redirect to plant dashboard"""
        self.logger.info("get headers")
        location = str(response.headers["Location"])
        location = location[2:][:-1]
        yield scrapy.Request(
            f"https://refu-log.com{location}",
            callback=self.parse_check_login,
            meta={
                "handle_httpstatus_list": [302],
            },
        )

    def parse_check_login(self, response):
        """Checks if login was successful"""

        self.logger.info("Check login")
        if self.debug:
            open_in_browser(response)

        login_xpath = response.xpath(
            '//*[@id="ctl00_ctl00_headerControl_lnkUserInfo"]'
        ).extract_first()
        id_link = response.xpath("//*[@id='aspnetForm']").attrib["action"]
        self.id_plant = id_link.replace("./PlantDetails.aspx?id=", "")
        self.logger.info(f"Plant ID: {self.id_plant}")
        if not login_xpath:
            self.logger.info("--> Login NOK")
            return {"login_status": "NOK"}

        self.logger.info("--> Login OK")
        yield {"login_status": "OK"}
        yield from self.parse_get_plant_info(response)

    def parse_get_plant_info(self, response):
        """Get plant info in the table"""

        xpath = "//*[@id='ctl00_ctl00_mainContentPlaceHolder_mainContentPlaceHolder_infoGridStatic_gridView']"
        table = response.xpath(xpath)
        self.logger.info("Extract plant infos")
        for row in table.xpath("//tr"):
            try:
                key = row.xpath("th//text()")[0].extract()
                value = row.xpath("td/span//text()")[0].extract()
                yield {DataReturn.PLANT_INFO: {key: value}}
            except:
                self.logger.error(f"Error to get plant_info data from row: {row}")
                pass
        yield from self.parse_fetch_data(response)

    def parse_fetch_data(self, response):
        """Get generation data for each month"""

        self.logger.info("Extract plant generate data")
        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br",
            "content-type": "application/json; charset=UTF-8",
            "referer": f"https://refu-log.com/PlantDetails.aspx?id={self.id_plant}",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
        }
        channel_list = [
            {
                "ChannelId": 5,
                "ChartData": [],
                "ChartInterval": 1,
                "Color": "DE2922",
                "ConfigurationId": 0,
                "DataType": 11,
                "DataTypeName": "Energy",
                "IsPlantDataAccessibleBasedOnLicense": True,
                "MeasureUnit": 5,
                "MeasureUnitCode": "kWh",
                "ParentSolarObjects": None,
                "SolarObject": {
                    "Firmware": None,
                    "Id": f"{self.id_plant}",  # Plant ID
                    "Name": "",
                    "Type": 0,
                },
                "Visible": True,
            }
        ]

        dt_start = self.dt_start.replace(day=1)
        dt_end = self.dt_end.replace(day=1)

        while dt_start <= dt_end:
            self.logger.info(dt_start)
            body = {
                "channels": channel_list,
                "year": dt_start.year,  # Year
                "month": dt_start.month,  # Month
                "day": dt_start.day,  # DAy
            }
            yield scrapy.Request(
                "https://refu-log.com/Ajax/StatisticsWebService.aspx/GetDataForChannels",
                method="POST",
                headers=headers,
                body=json.dumps(body),
                callback=self.parse_generation_data,
            )
            dt_start += timedelta(days=31)
            dt_start = dt_start.replace(day=1)

    def parse_generation_data(self, response):
        """Parse the generation data in the right format
        also pops date out of range
        """
        chart_data = json.loads(response.text)["d"][0]["ChartData"]
        self.logger.info(f"Generate data len: {len(chart_data)}")
        for data in chart_data:
            date_time = data["DateTime"]
            day = date(date_time["Year"], date_time["Month"], date_time["Day"])
            if day < self.dt_start or day > self.dt_end:
                pass
            value = data["Value"]["Value1"]
            yield {DataReturn.DATA: {day: value}}
