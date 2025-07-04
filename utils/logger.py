from copy import error

from datetime import datetime
import traceback
from typing import List

from settings.settings import settings
from utils.utils import Utils

class TXTLogger():
    
    @staticmethod
    def get_errors() -> List[str]:
        """Возвращает список строк из файла с ошибками

        Returns:
            List[str]: строки из файла с ошибками
        """
        
        links: List[str] = []
        try:
            with open(Utils.get_path(settings.ERROR), 'r', encoding="utf-8") as f:
                links = f.readlines()
        except:
            print("no file")
        return links
    
    @staticmethod
    def log_error(content = 'None', error: Exception = None):
        """Сохраняет логи в файл, указанную в настройках

        Args:
            content (str): лог
        """
        try:
            with open(Utils.get_path(settings.ERROR), 'a+', encoding="utf-8") as f:
                f.write(content + "\n")
        except Exception as e:
            print('Лог не готов: ', e)

        print(error)