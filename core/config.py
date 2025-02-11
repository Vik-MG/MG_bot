# config.py
import os
from dotenv import load_dotenv
from core.utils.logging_utils import setup_logger

# Настройка логирования
logger = setup_logger(__name__)

# Загрузка переменных окружения из .env файла
load_dotenv()

# Telegram Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("Переменная окружения BOT_TOKEN не задана!")
    raise ValueError("Переменная окружения BOT_TOKEN обязательна для работы приложения.")

VIBER_BOT_TOKEN = os.getenv("VIBER_BOT_TOKEN")

# Google API Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CREDENTIALS_FILE = "/etc/secrets/telegrambot4new-578a25fc7aa8.json"

if not CREDENTIALS_FILE:
    logger.error("Переменная окружения CREDENTIALS_FILE не задана!")
    raise ValueError("Переменная окружения CREDENTIALS_FILE обязательна для работы приложения.")
CREDENTIALS_FILE = os.path.join(BASE_DIR, CREDENTIALS_FILE)

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
if not SPREADSHEET_ID:
    logger.error("Переменная окружения SPREADSHEET_ID не задана!")
    raise ValueError("Переменная окружения SPREADSHEET_ID обязательна для работы приложения.")

# Google API Scope
GOOGLE_API_SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

logger.info("Конфигурация успешно загружена.")

