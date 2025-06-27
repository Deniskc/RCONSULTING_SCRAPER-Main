import json
import os
from datetime import datetime
from pathlib import Path

from settings.settings import settings


class Utils:
    @staticmethod
    def load_settings():
        """Загружает настройки из settings.json
        """
        with open('settings.json') as json_file:
            data = json.load(json_file)
            settings.EXCEL_FILE_NAME = data["EXCEL_FILE_NAME"] + ".xlsx"
            settings.URL = data["URL"]
            settings.ERROR = data["ERROR"]
            settings.MIN = data["MIN"]
            settings.MAX = data["MAX"]
            settings.DIRECTORY = data["DIRECTORY"]
            if settings.MIN >= settings.MAX:
                raise RuntimeError("Максимум должен быть строго больше минимума!")
            Utils.check_directory()

    @staticmethod
    def check_directory():
        """Создает папку в формате ГГГГ_ММ_ДД_ЧЧ_ММ_СС
        """
        base_path = Path(settings.DIRECTORY)
        base_path.mkdir(parents=True, exist_ok=True)
        
        folder_name = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        target_path = base_path / folder_name
        target_path.mkdir(exist_ok=True)  # Не добавляет _1, _2, если папка уже есть
        
        return str(target_path)

    @staticmethod
    def get_path(filename: str) -> str:
        """Возвращает путь к файлу внутри папки с датой
        """
        base_path = Path(settings.DIRECTORY)
        dated_folder = next(base_path.glob("*_*_*_*_*_*"), None)  # Ищем папку с датой
        
        if not dated_folder:  # Если папки нет (маловероятно, т.к. check_directory() её создает)
            dated_folder = Path(Utils.check_directory())
            
        return str(dated_folder / filename)