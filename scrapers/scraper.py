from typing import List, Union

from selenium import webdriver
from selenium.webdriver.common.by import By

import re
import abc
from time import sleep

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from datetime import datetime, timedelta
from utils.logger import TXTLogger

from utils.utils import Utils


class Scraper(abc.ABC):
    """Базовый (абстрактный) скрапер
    """
    
    __url__: str
    
    __driver__: webdriver.Chrome
    
    __logger__: TXTLogger
    
    def __init__(self, 
                 driver: webdriver.Chrome, 
                 url: str,
                 logger: TXTLogger = TXTLogger()
                 ) -> None:
        self.url = url
        self.driver = driver
        self.logger = logger
    
    @property
    def driver(self):
        return self.__driver__
    
    @property
    def url(self):
        return self.__url__
    
    @property
    def logger(self):
        return self.__logger__
    
    @driver.setter
    def driver(self, value: webdriver.Chrome):
        self.__driver__ = value
    
    @url.setter
    def url(self, value: str):
        self.__url__ = value
    
    @logger.setter
    def logger(self, value: TXTLogger):
        self.__logger__ = value
    
    @abc.abstractmethod
    def process(self):
        """Парсит страничку
        """

        print(f"Текущий URL: {self.driver.current_url}")
        print(f"Заголовок страницы: {self.driver.title}")

        None
    
    @abc.abstractmethod
    def save_pictures(self, prefix: Union[str, int]) -> List[str]:
        """Сохраняет картинки из объявления

        Args:
            prefix (Union[str, int]): название картинок (общий префикс)

        Returns:
            List[str]: список путей до картинок
        """
        None
    
    def __save_page__(self, id: int) -> str:
        """Сохраняет страницу

        Args:
            id (int): id страницы

        Returns:
            str: путь до сохраненной страницы
        """
        
        ## prepare full size
        original_size = self.driver.get_window_size()
        required_height = self.driver.execute_script('return document.body.parentNode.scrollHeight')
        self.driver.set_window_size(original_size['width'], required_height * 1.5)
        
        ## screenshooting
        path: str = Utils.get_path(f"{id}_объявление.png")
        self.driver.find_element(by=By.TAG_NAME, value='body').screenshot(path)
        
        ## reset
        self.driver.set_window_size(original_size['width'], original_size['height'])
        
        return path
            
    def __save_image__(self, prefix: Union[int, str], no: int) -> str:
        """Делает скриншот

        Args:
            prefix (Union[int, str]): название скриншота
            no (int): номер скриншота

        Returns:
            str: путь до скриншота
        """
                
        sleep(2) #render
        path = Utils.get_path(f"{prefix}_{no}.png")
        self.driver.save_screenshot(path)
        return path
    
    def __get_page_link__(self, marker: str, no: int) -> str:
        if "?" in self.url:
            if f"?{marker}=" in self.url or f"&{marker}=" in self.url:
                parts = re.split('?|&', self.url)
                url = ""
                for n, part in enumerate(parts):
                    if part.startswith(marker):
                        part = f"{marker}={no}"
                    if n == 0:
                        url = part
                    elif n == 1:
                        url = url + "?" + part
                    else:
                        url = url + "&" + part
            else:
                return f"{self.url}&{marker}={no}"
        else:
            return f"{self.url}?{marker}={no}"
    
    def __save_media__(self, id: int, published_on: str, url: str):
        """Сохраняет скриншоты объявления и фотографий

        Args:
            id (int): id объявления
            published_on (str): дата публикации
        """
        
        page_screen_path = self.__save_page__(id=id)
        picture_paths = list() #self.save_pictures(prefix=id) ## to save pics 
        picture_paths.append(page_screen_path)
        pictures_and_stamps = {picture_path: published_on for picture_path in picture_paths}
        self._Timestamper().timestamp_all(pictures_and_stamps, id, url)


        print(f"Сохранение медиа для ID {id}. Пути: {picture_paths}")
    
    class _Timestamper():
        """Проставляет метку времени на изображениях
        """
        
        FONT: str
        
        def __new__(cls):
            if not hasattr(cls, "instance"):
                cls.instance = super().__new__(cls)
                cls.FONT = ImageFont.truetype("arial.ttf", 30)
                return cls.instance
            else:
                return cls.instance
        
        def timestamp(self, picture_path: str, timestamp: str, url: str):
            """Ставит метку времени на одном скриншоте

            Args:
                picture_path (str): путь до скриншота
                timestamp (str): метка времени
            """
            
            img = Image.open(picture_path)
            I1 = ImageDraw.Draw(img)
            I1.text((10, 10), timestamp, font=self.FONT, fill=(255, 0, 0))
            I1.text((10, 50), url, font=self.FONT, fill=(255, 0, 0))
            img.save(picture_path)
            
        def timestamp_all(self, pictures_and_timesmps: dict[str, str], id: int, url: str):
            """Ставить метки времени на нескольких скриншотах

            Args:
                pictures_and_timesmps (dict[str, str]): словарь формата {путь до файла: метка времени}
            """
            
            for item in pictures_and_timesmps.items():
                self.timestamp(item[0], item[1], url)
    
    class DateConverter():
        """Конвертер для строкового представления данных
        """
        
        def __new__(cls):
            if not hasattr(cls, "instance"):
                cls.instance = super().__new__(cls)
                return cls.instance
            else:
                return cls.instance
        
        @staticmethod
        def yeild_date_DD_MM_YYYY(published_on: str) -> str:
            
            if "сегодня" in published_on:
                return datetime.strftime(datetime.now(), "%Y-%m-%d")
            elif "позавчера" in published_on:
                return datetime.strftime(datetime.now() - timedelta(2), "%Y-%m-%d")
            elif "вчера" in published_on:
                return datetime.strftime(datetime.now() - timedelta(1), "%Y-%m-%d")
            else:
                date_parts = published_on.split(" ")
                day, month = int(date_parts[0]), Scraper.DateConverter.__month_to_num__(date_parts[1])
                
                # Проверяем, если наступил новый год
                year = datetime.now().year if datetime.now().month >= month else (datetime.now().year - 1)
                
                return datetime.strftime(datetime(day=day, month=month, year=year), "%Y-%m-%d")   

        @staticmethod
        def __month_to_num__(month: str) -> int:
            if "янв" in month:
                return 1
            elif "фев" in month:
                return 2
            elif "мар" in month:
                return 3
            elif "апр" in month:
                return 4
            elif "ма" in month:
                return 5
            elif "июн" in month:
                return 6
            elif "июл" in month:
                return 7
            elif "авг" in month:
                return 8
            elif "сен" in month:
                return 9
            elif "окт" in month:
                return 10
            elif "ноя" in month:
                return 11
            elif "дек" in month:
                return 12
            else:
                return 0