# core/utils/google_utils.py
from core.utils.logging_utils import setup_logger
from oauth2client.service_account import ServiceAccountCredentials
from gspread import authorize
from gspread.exceptions import APIError, WorksheetNotFound
from core.config import CREDENTIALS_FILE, GOOGLE_API_SCOPE

# Настройка логгера
logger = setup_logger(__name__)

def get_google_client():
    """Создаёт и возвращает клиента Google API.

    Returns:
        gspread.Client: Авторизованный клиент Google API.
    """
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_FILE, GOOGLE_API_SCOPE
        )
        client = authorize(credentials)
        logger.info("Google API клиент успешно авторизован.")
        return client
    except Exception as e:
        logger.error(f"Ошибка авторизации Google API: {e}", exc_info=True)
        raise

def handle_google_api_error(func):
    """Декоратор для обработки ошибок Google API.

    Args:
        func (callable): Функция, для которой требуется обработка ошибок.

    Returns:
        callable: Обёрнутая функция.
    """
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except APIError as e:
            logger.error(f"Ошибка Google API: {e}", exc_info=True)
            raise
        except WorksheetNotFound as e:
            logger.warning(f"Лист не найден: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Неизвестная ошибка Google API: {e}", exc_info=True)
            raise
    return wrapper

def format_data_for_sheets(data):
    """Подготавливает данные для загрузки в Google Sheets.

    Args:
        data (list[dict]): Список словарей данных.

    Returns:
        list[list]: Форматированный двумерный массив данных.
    """
    try:
        formatted_data = [list(entry.values()) for entry in data]
        logger.debug(f"Данные успешно отформатированы для загрузки в Google Sheets: {formatted_data}")
        return formatted_data
    except Exception as e:
        logger.error(f"Ошибка при форматировании данных: {e}", exc_info=True)
        raise
