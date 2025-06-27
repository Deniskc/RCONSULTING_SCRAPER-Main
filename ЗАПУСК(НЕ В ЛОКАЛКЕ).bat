@echo off
REM \\x64\public\ПАРСЕР\RCONSULTING_SCRAPER-Main\venv
set VENV_DIR=venv

REM Проверка существования виртуального окружения
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo Виртуальное окружение не найдено в %VENV_DIR%
    pause
    exit /b 1
)

REM Активация виртуального окружения
call %VENV_DIR%\Scripts\activate.bat

REM Запуск main.py
python main.py

REM Держим окно открытым после завершения (опционально)
pause