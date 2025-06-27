from typing import Dict, Iterator, List, Union
import pandas as pd
import random

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException


from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time


from random import randint
from time import sleep

from scrapers.scraper import Scraper
from settings.settings import settings
from utils.utils import Utils


class AvitoScraper(Scraper):
    
    def process(self):
        try:
            scraped_items: List[Dict[str, str]] = list()
            
            self.driver.get(url=self.url)
            
            try:
                for page_url in self.get_page_urls():
                    scraped_items.extend(self.scrape_page(page_url))
            except Exception as e:
                print(e)
                try:

                    time.sleep(5)
                    for page_url in self.get_page_urls():
                        scraped_items.extend(self.scrape_page(page_url))
                except Exception as e1:
                    print(e1)

            
            links: List[Dict[str, str]] = self.process_links(links=self.logger.get_errors())
            scraped_items.extend(links)
            
            self._AvitoWriter().dump(items=scraped_items)
        except Exception as e:
            print(e)
            try:
                time.sleep(5)
                self._AvitoWriter().dump(items=scraped_items)
            except Exception as e1:
                print(e1)

    
    def process_links(self, links: List[str]) -> List[Dict[str, str]]:
        """Парсит список ссылок на объявления
        """
        
        if settings.TESTING == True:
            scraped_items = []
            success_count = 0  # Счетчик успешных записей
    
            for l in links:
                try:
                    sleep(randint(settings.MIN, settings.MAX))
                    
                    if settings.TESTING and success_count >= 1200:
                        try:
                            self._AvitoWriter().dump(items=scraped_items, table_filename='test.xlsx')

                        except Exception as e:
                            self.logger.log_error(f"Ошибка при сохранении Excel: {str(e)}")
                        return scraped_items
                        
                    item = self.scrape_item(l)
                    if item:
                        scraped_items.append(item)
                        success_count += 1
                        
                except Exception as e:
                    self.logger.log_error(error=e)
            
            # return scraped_items
        else:
            scraped_items: List[Dict[str, str]] = list()

            for l in links:
                sleep(randint(settings.MIN, settings.MAX))
                try:
                    scraped_items.append(self.scrape_item(l))

                except:
                    self.logger.log_error(l)

        return scraped_items
    
    def get_page_urls(self) -> Iterator[str]:
        """Возвращает ссылки на страницы со списком объявлений
        """
        
        try: 
            last_page_index: int = self.get_last_page_index()
            for p in range(1, last_page_index + 1):
                yield self.__get_page_link__(marker=settings.AVITO_PAGE_MARKER, no=p)
        except:
            self.logger.log_error(self.url)
            yield self.url
        
    def scrape_page(self, page_link: str) -> List[Dict[str, str]]:
        """Парсит страницу с объявлениями
        """
        
        self.driver.get(page_link)
        
        link_wrappers = self.driver.find_elements(by=By.XPATH, value=settings.AVITO_LINK_ITEMS_XPATH)
        links: List[str] = [link.get_attribute("href") for link in link_wrappers]


        return self.process_links(links=links)
    
    def scrape_item(self, link: str) -> Dict[str, str]:
        """Парсит объявление
        """
        
        if not link or not link.startswith(('http://', 'https://')):
            print(f"Пропускаем неверную ссылку: {link}")
            return None

        self.driver.get(link)

        try:

            footer = self.driver.find_element(by=By.XPATH, value=settings.AVITO_ITEM_FOOTER)

        
            id = footer \
                                    .find_element(by=By.XPATH, value=settings.AVITO_FOOTER_ID_XPATH) \
                                    .text \
                                    .removeprefix("№") \
                                    .strip()
            published_on = footer \
                                    .find_element(by=By.XPATH, value=settings.AVITO_FOOTER_PUBLISHED_ON_XPATH) \
                                    .text \
                                    .replace("·", "") \
                                    .strip()

                                    
            published_on = AvitoScraper.DateConverter.yeild_date_DD_MM_YYYY(published_on=published_on)

            # title = self.driver  \
            #                        .find_element(by=By.XPATH, value=settings.AVITO_TITLE_XPATH) \
            #                        .text\
            # seller_type = self.driver.find_element(by=By.XPATH, value=settings.AVITO_SELLER_TYPE_XPATH) \
            #                        .text
            
            price = self.driver \
                                    .find_element(by=By.XPATH, value=settings.AVITO_PRICE_XPATH) \
                                    .text
            
            price_per_meter = "Не указана"  # Значение по умолчанию
            try:
                price_per_meter = self.driver \
                                        .find_element(by=By.XPATH, value=settings.AVITO_SUBPRICE_XPATH) \
                                        .text
            except NoSuchElementException: # type: ignore
                pass
                                    
            contact = self.driver.find_element(by=By.XPATH, value=settings.AVITO_SELLER_XPATH) \
                                    .text
                                    

                                    
            address = self.driver.find_element(by=By.XPATH, value=settings.AVITO_ADDRESS_XPATH) \
                                    .text
            
            try:
                address_georef = self.driver \
                                    .find_element(by=By.XPATH, value=settings.AVITO_GEOREF_XPATH) \
                                    .text
            except:
                address_georef = ""
                
            description_items = self.driver \
                                    .find_elements(by=By.XPATH, value=settings.AVITO_DESCR_XPATH)
                                    
            description = " ".join([d.text for d in description_items])
            
            usecase = self.driver \
                                    .find_element(by=By.XPATH, value=settings.AVITO_USECASE_XPATH) \
                                    .text
                                    
            
            info_block = self.driver \
                                    .find_elements(by=By.XPATH, value=settings.AVITO_INFO1_XPATH) \
            
            info_block2 = self.driver \
                                    .find_elements(by=By.XPATH, value=settings.AVITO_INFO2_XPATH)
            
            info_block.extend(info_block2)
            
            other = self.__get_other_info__(info_block)
            
            self.__save_media__(id, published_on, link)
            self.save_tel(id=id, timestamp=published_on, url=link)

            dct = self._AvitoWriter().to_avito_data(
                                                    link, 
                                                    id, 
                                                    published_on, 
                                                    price, 
                                                    price_per_meter, 
                                                    contact, 
                                                    address, 
                                                    address_georef, 
                                                    description, 
                                                    usecase, 
                                                    other
                                                    )
            

        except Exception as e:
            self.logger.log_error(error=e, content="Ошибка при парсинге элемента")
            return {}

        return dct
        
    def __get_other_info__(self, info_block: List[WebElement]) -> Dict[str, str]:
        keys: List[str] = list()
        values: List[str] = list()                  
        for el in info_block:
            key, value = el.text.split(":")
            keys.append(key.strip())
            values.append(value.strip())
            
        other = dict(zip(keys, values))
        
        return other
    
    def __save_page__(self, id: int) -> str:
        pagefile = super().__save_page__(id)
        return pagefile

    def save_tel(self, id: int, timestamp: str, url: str):
        try:
            self.driver.find_element(by=By.XPATH, value=settings.AVITO_BTN_XPATH).click()
            tel = self.__save_image__(id, "tel")
            self._Timestamper().timestamp(picture_path=tel, timestamp=timestamp, url=url)
        except:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, settings.AVITO_BTN_XPATH)))
            self.driver.find_element(by=By.XPATH, value=settings.AVITO_BTN_XPATH).click()
            tel = self.__save_image__(id, "tel")
            self._Timestamper().timestamp(picture_path=tel, timestamp=timestamp, url=url)
    
    def save_pictures(self, prefix: Union[str, int]) -> List[str]:
        paths: List[str] = []
        
        try:

            # Ожидание и клик на главное изображение с обработкой перехвата
            main_image = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, settings.AVITO_MAIN_PIC_XPATH))
            )
            
            # Способ 1: Прокрутка к элементу перед кликом
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", main_image)
                ActionChains(self.driver).move_to_element(main_image).pause(1).click().perform()
                
            # Способ 2: Клик через JavaScript (альтернатива)
            except:
                self.driver.execute_script("arguments[0].click();", main_image)
            
            path = self.__save_image__(prefix, 0)
            paths.append(path)
            
            # Ожидание загрузки галереи
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located((By.XPATH, settings.AVITO_ON_EXTENDED_PIC_XPATH))
            )
            
            pictures = self.driver.find_elements(By.XPATH, settings.AVITO_ON_EXTENDED_PIC_XPATH)
            
            for no, img in enumerate(pictures, start=1):
                try:
                    # Прокрутка и клик с ожиданием
                    self.driver.execute_script("arguments[0].scrollIntoView();", img)
                    WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(img))
                    img.click()
                    time.sleep(0.5)  # Небольшая пауза для стабилизации
                    path = self.__save_image__(prefix, no)
                    paths.append(path)
                except Exception as e:
                    print(f"Не удалось обработать изображение {no}: {str(e)}")
                    continue
                    
        except TimeoutException:
            print("Таймаут при ожидании элементов галереи")
        except Exception as e:
            print(f"Критическая ошибка при сохранении изображений: {str(e)}")
        
        return paths
        
    def get_last_page_index(self) -> int:
        """Возвращает количество страниц
        """
        
        last_page_index = self.driver \
                            .find_element(by=By.XPATH, value=settings.AVITO_NUM_PAGE_XPATH) \
                            .text
                                          
        return int(last_page_index) if last_page_index.isnumeric() else 0
    
    class _AvitoWriter():

        def __new__(cls):
            if not hasattr(cls, "instance"):
                cls.instance = super().__new__(cls)
                return cls.instance
            else:
                return cls.instance

        def dump(self, items: List[Dict[str, str]], table_filename='nedvizka.xlsx') -> bool:
            
            lst = []
            if len(items) > 0:
                lst.append(list(items[0].keys()))
            else:
                return False
            

            try:
                items.sort(key=lambda x: x.get("ID объявления", ""))
            except Exception as e:
                print(e)

            lst = [list(item.values()) for item in items]
            df = pd.DataFrame(lst)
            
            writer = pd.ExcelWriter(Utils.get_path(table_filename))
            df.to_excel(writer, sheet_name='welcome', index=False)
            writer.close()
            return True

        def to_avito_data(self, 
                          link, 
                          id, 
                          published_on, 
                          price, 
                          price_per_meter, 
                          contact, 
                          address, 
                          address_georef, 
                          description,
                          usecase, 
                          other):
            
            dct: Dict[str, str] = dict()
            dct["ID объявления"] = id
            dct["Тип"] = usecase
            dct["Адрес"] = address
            dct["Район"] = address_georef
            dct["Цена"] = price
            dct["Цена/метр"] = price_per_meter
            dct["Продавец"] = contact
            dct["Описание"] = description
            dct["Дата"] = published_on
            dct["Ссылка"] = link
            dct.update(other)
            return dct
