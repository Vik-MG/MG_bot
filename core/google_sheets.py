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

logger = setup_logger(__name__)

def get_creds():
    """Возвращает учетные данные для Google API."""
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE, GOOGLE_API_SCOPE
    )
    return credentials
# Инициализация менеджера клиента Google Sheets
agcm = AsyncioGspreadClientManager(get_creds)

@handle_google_api_error
async def get_google_sheet(sheet_name="Лист1") -> AsyncioGspreadWorksheet:
    """Возвращает лист Google Sheets или создаёт его, если он отсутствует."""
    try:
        if not CREDENTIALS_FILE or not SPREADSHEET_ID:
            raise ValueError("Отсутствует CREDENTIALS_FILE или SPREADSHEET_ID.")

        client = await agcm.authorize()
        spreadsheet: AsyncioGspreadSpreadsheet = await client.open_by_key(SPREADSHEET_ID)

        try:
            worksheet: AsyncioGspreadWorksheet = await spreadsheet.worksheet(sheet_name)
        except Exception:
            worksheet = await spreadsheet.add_worksheet(title=sheet_name, rows=100, cols=20)
            logger.info(f"Создан новый лист: {sheet_name}.")
        
        return worksheet
    except Exception as e:
        logger.error(f"Ошибка доступа к Google Sheet: {e}", exc_info=True)
        raise RuntimeError("Не удалось получить доступ к Google Sheet.")

@handle_google_api_error
async def initialize_google_sheet(sheet: AsyncioGspreadWorksheet, headers: list):
    """Проверяет заголовки, обновляет только если необходимо."""
    try:
        existing_headers = await sheet.row_values(1)
        existing_headers = [header.strip() for header in existing_headers]
        headers = [header.strip() for header in headers]

        if existing_headers == headers:
            logger.info(f"Заголовки листа '{sheet.title}' совпадают, обновление не требуется.")
            return

        if not existing_headers:
            await sheet.append_row(headers)  # Если таблица пустая, записываем заголовки
            logger.info(f"Добавлены заголовки в '{sheet.title}': {headers}")
        else:
            await sheet.update(f"A1:{chr(64 + len(headers))}1", [headers])  # Обновляем первую строку
            logger.info(f"Заголовки обновлены: {headers}")

    except Exception as e:
        logger.error(f"Ошибка обновления заголовков в '{sheet.title}': {e}", exc_info=True)
        raise RuntimeError(f"Не удалось обновить заголовки в Google Sheet '{sheet.title}'.")

@handle_google_api_error
async def update_client_status(sheet_name: str, client_id: str, status: str):
    """Обновляет статус клиента в таблице Google Sheets."""
    worksheet = await get_google_sheet(sheet_name)
    all_data = await worksheet.get_all_values()

    if not all_data:
        logger.error(f"Лист '{sheet_name}' пуст, статус обновить невозможно.")
        return False

    headers = all_data[0]
    try:
        status_col_index = headers.index("Статус") + 1  # Столбцы в Google Sheets нумеруются с 1
    except ValueError:
        logger.error(f"Столбец 'Статус' не найден в '{sheet_name}'.")
        return False

    for i, row in enumerate(all_data[1:], start=2):  # Начинаем со второй строки
        if len(row) > 1 and str(row[1]).strip() == str(client_id).strip():  # Проверяем ID клиента
            cell = f"{chr(64 + status_col_index)}{i}"  # Определяем ячейку для обновления
            await worksheet.update(cell, [[status]])  # Обновляем статус
            logger.info(f"✅ Статус клиента {client_id} обновлён на '{status}' в {sheet_name}.")
            return True

    logger.warning(f"⚠ Клиент {client_id} не найден в таблице {sheet_name}.")
    return False
