from time import sleep
from typing import List, Union
from selenium.webdriver.common.by import By
import pandas as pd

from scrapers.scraper import Scraper
from settings.settings import settings


class CianScraper(Scraper):
    
    def process(self):
        
        self.driver.get(url=self.url)
        
        ## Download Excel file
        download_buttons = self.driver.find_element(by=By.XPATH, value=settings.CIAN_DOWNLOAD_EXCEL_BTN_XPATH)
        download_buttons.click()
        
        # Wait to download 
        sleep(10)
        
        df = pd.read_excel(f"{settings.DIRECTORY}/{settings.CIAN_EXCEL_FILE}")
        
        links: List[str] = df[settings.CIAN_EXCEL_LINK_HEADER].to_list()
        ids: List[int] = list(map(int, df[settings.CIAN_ID_HEADER].to_list()))
        
        df[settings.CIAN_ID_HEADER] = df[settings.CIAN_ID_HEADER].astype(int)
        df[settings.CIAN_LAST_UPDATE_COL_TITLE] = ""
        
        for link, id in zip(links, ids):
            self.driver.get(link)
            published_block = self.driver.find_element(by=By.XPATH, value=settings.CIAN_DATE_XPATH)
             
            published_text = published_block.text.split(":")[1].strip()     
            published_on = CianScraper.DateConverter.yeild_date_DD_MM_YYYY(published_on=published_text)
            
            df.loc[df[settings.CIAN_ID_HEADER] == id, settings.CIAN_LAST_UPDATE_COL_TITLE] = published_on
            
            self.__save_media__(id=id, published_on=published_on, url=link)
        
        df.to_excel(f"{settings.DIRECTORY}/{settings.CIAN_EXCEL_FILE}")
        
    def __save_page__(self, id: int):
        
        self.__save_pdf__()
        
        ## Save as Screenshot
        return super().__save_page__(id)

    def __save_pdf__(self):
        link = self.driver.find_element(by=By.XPATH, value=settings.CIAN_PDF_LINK_XPATH).get_attribute("href")
        url = self.driver.current_url
        self.driver.get(link)
        self.driver.get(url)
        
    def save_pictures(self, prefix: Union[str, int]) -> List[str]:
        
        paths: List[str] = list()
        
        ## GET IMAGES
        pictures = self.driver.find_elements(by=By.XPATH, value=settings.CIAN_IMAGE_XPATH)
        links: List[str] = [pic.get_attribute("src") for pic in pictures]
        
        ## SAVE
        for no, link in enumerate(links):
            self.driver.get(link)
            path = self.__save_image__(prefix, no+1)
            paths.append(path)
        
        return paths