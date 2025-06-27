from selenium import webdriver

from scrapers.builders.driver_builder import driver_builder

from scrapers.avito_scraper import AvitoScraper
from scrapers.cian_scraper import CianScraper
from scrapers.scraper import Scraper

from settings.settings import settings


def yield_scraper() -> Scraper:
    """Возвращает нужный скрапер, основываясь на URL в настройках

    Raises:
        ValueError: Если сайт не поддерживается

    Returns:
        Scraper: скрапер для сайта
    """
    
    driver: webdriver.Chrome = driver_builder.yield_driver()
    if "avito" in settings.URL[:20]:
        return AvitoScraper(driver=driver, url=settings.URL)
    elif "cian" in settings.URL[:20]:
        return CianScraper(driver=driver, url=settings.URL)
    else:
        raise ValueError("Неправильная ссылка")