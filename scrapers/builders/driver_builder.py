from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium_stealth import stealth
import json

from settings.settings import settings


class driver_builder:
    """Фабрика selenium-драйверов для браузера
    """

    def yield_driver() -> webdriver.Chrome:
        """Возвращает драйвер для работы с Хромом

        Returns:
            webdriver.Chrome: Драйвер для Хрома
        """

        
        options = webdriver.ChromeOptions()
        
        options.binary_location = '/usr/bin/google-chrome' 
        
        chrome_prefs = {
            "download.prompt_for_download": False,
            "profile.default_content_settings.popups": 0,
            "download.default_directory": settings.DIRECTORY,
            "savefile.default_directory": settings.DIRECTORY,
        }
        
       
        options.add_argument("--headless=new")
        
        options.add_experimental_option("prefs", chrome_prefs)

        # start the browser window in maximized mode
        options.add_argument('--start-maximized')

        # disable extensions
        options.add_argument('--disable-extensions')

        options.add_argument('--log-level=3')

        # disable sandbox mode
        options.add_argument('--no-sandbox')

        # disable shared memory usage
        options.add_argument('--disable-dev-shm-usage')
        # options.page_load_strategy = 'eager'
        
        # service = ChromeService(executable_path=ChromeDriverManager().install())
        service = ChromeService()
        
        driver = webdriver.Chrome(options=options, service=service)
        
        driver.maximize_window()
        
        stealth(
            driver=driver,
            languages=["ru-RU", "ru"],
            vendor="Google Inc.",
            platform="Win64",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True
        )
        
        return driver
