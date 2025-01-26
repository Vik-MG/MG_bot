# google_sheets.py
"""
core/google_sheets.py

Модуль для взаимодействия с Google Sheets.
- Подключение к Google Sheets.
- Получение или создание листа.
- Инициализация структуры заголовков листа.
"""

import asyncio
from gspread_asyncio import AsyncioGspreadClientManager, AsyncioGspreadSpreadsheet, AsyncioGspreadWorksheet
from core.config import CREDENTIALS_FILE, GOOGLE_API_SCOPE, SPREADSHEET_ID
from core.utils.logging_utils import setup_logger
from core.utils.google_utils import handle_google_api_error
from oauth2client.service_account import ServiceAccountCredentials

# Настройка логгера
logger = setup_logger(__name__)

def get_creds():
    """
    Возвращает учетные данные для Google API.
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE, GOOGLE_API_SCOPE
    )
    return credentials

# Инициализация менеджера клиента Google Sheets
agcm = AsyncioGspreadClientManager(get_creds)

@handle_google_api_error
async def get_google_sheet(sheet_name="Лист1") -> AsyncioGspreadWorksheet:
    """
    Асинхронно подключается к Google Sheets и возвращает указанный лист.
    Если листа не существует, он будет создан.

    Args:
        sheet_name (str): Имя листа для получения.

    Returns:
        AsyncioGspreadWorksheet: Указанный лист.
    """
    try:
        if not CREDENTIALS_FILE or not SPREADSHEET_ID:
            raise ValueError("Отсутствует CREDENTIALS_FILE или SPREADSHEET_ID.")

        client = await agcm.authorize()
        logger.info("Успешно выполнена аутентификация с Google API.")

        spreadsheet: AsyncioGspreadSpreadsheet = await client.open_by_key(SPREADSHEET_ID)
        logger.info(f"Таблица '{SPREADSHEET_ID}' успешно открыта.")

        try:
            worksheet: AsyncioGspreadWorksheet = await spreadsheet.worksheet(sheet_name)
            logger.info(f"Лист '{sheet_name}' найден.")
        except Exception:
            worksheet = await spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=20)
            logger.info(f"Лист '{sheet_name}' не найден. Создан новый лист.")
        
        return worksheet
    except Exception as e:
        logger.error(f"Ошибка доступа к Google Sheet: {e}", exc_info=True)
        raise RuntimeError("Не удалось получить доступ к Google Sheet.")

@handle_google_api_error
async def initialize_google_sheet(sheet: AsyncioGspreadWorksheet, headers: list):
    """
    Асинхронно проверяет или обновляет заголовки Google Sheets.

    Args:
        sheet (AsyncioGspreadWorksheet): Лист Google Sheets.
        headers (list): Ожидаемые заголовки.
    """
    try:
        existing_headers = await sheet.row_values(1)
        if existing_headers != headers:
            await sheet.clear()
            await sheet.append_row(headers)
            logger.info(f"Заголовки листа '{sheet.title}' обновлены: {headers}")
    except Exception as e:
        logger.error(f"Ошибка обновления заголовков в листе '{sheet.title}': {e}", exc_info=True)
        raise RuntimeError(f"Не удалось обновить заголовки в Google Sheet '{sheet.title}'.")
