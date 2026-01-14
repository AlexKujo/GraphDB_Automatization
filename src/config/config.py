"""Конфигурация приложения"""
import os
from pathlib import Path

# Базовый путь проекта
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Пути к файлам конфигурации
GOOGLE_SHEETS_CREDENTIALS_PATH = PROJECT_ROOT / "src" / "config" / "googlesheets_credentials.json"
ENV_FILE_PATH = PROJECT_ROOT / "src" / "config" / ".env"

# Пути к директориям
IMAGES_DIR = PROJECT_ROOT / "images"
DATA_DIR = PROJECT_ROOT / "data"

# Создаем директории если их нет
IMAGES_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

