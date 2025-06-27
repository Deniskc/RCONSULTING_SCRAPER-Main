from settings.settings import settings
from utils.utils import Utils
from scrapers.scraper import Scraper
from scrapers.builders.func.yield_scraper import yield_scraper


from selenium.webdriver.remote.remote_connection import LOGGER
import logging
logging.basicConfig(level=logging.INFO, filename='parser.log', filemode='w')
LOGGER.setLevel(logging.WARNING)


def main():
    # scraper: Scraper = yield_scraper()


    print(f"Директория для сохранения: {settings.DIRECTORY}")
    print(f"URL: {settings.URL}")


    import traceback
    try:
        Utils.load_settings()
        print("Загрузка настроек...")
        
        scraper: Scraper = yield_scraper()
        print("Инициализация парсера...")
        
        scraper.process()
        print("Запуск процесса парсинга...")
        
        scraper.driver.quit()
        print("Завершение работы...")
        print("Готово! Проверьте папку:", settings.DIRECTORY)
            
    except Exception as e:
        print("Ошибка при выполнении:")
        traceback.print_exc()
        if 'scraper' in locals():
            scraper.driver.quit()


    # scraper.process()
    # scraper.driver.quit()


if __name__ == "__main__":
    Utils.load_settings()
    main()
