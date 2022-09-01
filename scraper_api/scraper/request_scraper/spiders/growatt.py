
"""Spider to fetch data from Growatt.com using their API
"""

import time
from datetime import date, timedelta

import crochet
from growattServer import GrowattApi, Timespan
from scraper_api.scraper.request_scraper.spiders.base_spider import BaseSpider
from scraper_api.validations import DataReturn

crochet.setup()
class Growatt(BaseSpider):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.api = GrowattApi()
        self.list_threads = []
        
       
    def check_login(self):
        """Checks if login is OK"""
        response = self.api.login(self.user_login, self.password)
        self.status_login = 'OK' if response['success'] else 'NOK'
        if not self.status_login:
            return
        
        self.user_id = response['user']['id']
        self.logger.info(f'user_id: {self.user_id}')
        
        response = self.api.plant_list(self.user_id)
        self.plant_info = response['data'][0]
        self.plant_id = self.plant_info['plantId']
        self.logger.info(f'plant_id: {self.plant_id}')
        
    def get_plant_info(self):
        """General plant info"""
        self.logger.info(f'get plant info')
        self.response = self.api.get_plant_settings(self.plant_id)
        
        list_keys = ['nominalPower','plant_lng','plant_lat','city','country']
        for key in list_keys:
            self.plant_info[key] = self.response.get(key, '')
    
    @crochet.run_in_reactor
    def request_generation_data(self, dt):
        """Run each response inside of a parallel reactor

        It will add the date in list_threads and remove it when
        it finishes, in this way the script knows when all the threads are over.
        """
        self.list_threads.append(dt)
        response = self.api.plant_detail(self.plant_id, Timespan.month, dt)
        for key in response['data'].keys():
            day = date(dt.year, dt.month, int(key))
            if day < self.dt_start or day > self.dt_end:
                continue
            dict_temp = {day:response['data'][key]}
            self.data_return.update({DataReturn.DATA:dict_temp})
        self.list_threads.remove(dt)
    
    def run_generation_data(self):
        """Fetch generation data
        """
        dt_start = self.dt_start.replace(day=1)
        dt_end = self.dt_end.replace(day=1)

        while dt_start <= dt_end:
            self.logger.info(dt_start)
            self.request_generation_data(dt_start)
            dt_start += timedelta(days=31)
            dt_start = dt_start.replace(day=1)
        
        for _ in range(15):
            time.sleep(2)
            if not self.list_threads:
                return
            self.logger.info(f'# Running Threads: {len(self.list_threads)}')
            self.logger.debug(self.list_threads)
        assert False, f"Time out threads: {len(self.list_threads)}"
        
    def run(self):
        """Calleble to run the spider"""
        self.check_login()
        self.logger.info(f'status_login: {self.status_login}')
        if not self.status_login:
            return
        self.data_return.update({DataReturn.LOGIN_STATUS: self.status_login})
        
        self.get_plant_info()
        self.data_return.update({DataReturn.PLANT_INFO: self.plant_info})
        self.run_generation_data()
        