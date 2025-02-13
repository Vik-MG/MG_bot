# core.google_drive.py
import os
import asyncio
from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds
from core.config import CREDENTIALS_FILE, SPREADSHEET_ID
from core.google_sheets import get_google_sheet
from core.utils.logging_utils import setup_logger

logger = setup_logger(__name__)

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

async def get_authenticated_client():
    """Аутентификация в Google API."""
    creds = ServiceAccountCreds.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    return Aiogoogle(service_account_creds=creds)

async def create_drive_folder(client: Aiogoogle, folder_name: str):
    """Создаёт папку в Google Drive."""
    async with client as g_client:
        drive_service = await g_client.discover("drive", "v3")
        request = await g_client.as_service_account(
            drive_service.files.create(json={"name": folder_name, "mimeType": "application/vnd.google-apps.folder"})
        )
        return request["id"]

async def upload_file(client: Aiogoogle, file_path: str, folder_id: str):
    """Загружает файл в Google Drive."""
    file_name = os.path.basename(file_path)
    mime_type = "application/octet-stream"

    async with client as g_client:
        drive_service = await g_client.discover("drive", "v3")

        metadata = {"name": file_name, "parents": [folder_id]}
        with open(file_path, "rb") as f:
            file_content = f.read()

        request = await g_client.as_service_account(
            drive_service.files.create(json=metadata, data=file_content, upload_type="multipart", fields="id")
        )

        logger.info(f"Файл {file_name} загружен в Google Drive. ID: {request['id']}")
        return request["id"]

async def upload_files_to_drive(client_id: str):
    """Загружает файлы клиента в Google Drive, если они ещё не загружены."""
    
    if not client_id:
        logger.error("❌ Ошибка: client_id не определён.")
        return
    
    try:
        # Подключаемся к Google Sheets
        sheet = await get_google_sheet("Розничные клиенты")
        data = await sheet.get_all_values()
        headers = data[0]
        rows = data[1:]

        # Ищем клиента по client_id
        # Отладка: печатаем все строки, чтобы проверить их структуру
        for row in rows:
            logger.debug(f"Проверяем строку Google Sheets: {row}")

        client_row = next((row for row in rows if str(row[1]) == str(client_id)), None)
        
        if not client_row:
            logger.warning(f"Клиент {client_id} не найден в Google Sheets.")
            return

        # Проверяем статус
        status_index = headers.index("Статус")
        if client_row[status_index] != "Новый":
            logger.info(f"Файлы клиента {client_id} уже загружены.")
            return

        # Создаём папку в Google Drive
        client = await get_authenticated_client()
        folder_id = await create_drive_folder(client, f"Клиент_{client_id}")

        # Загружаем файлы
        upload_folder = os.path.join("uploads", client_id)
        if not os.path.exists(upload_folder):
            logger.warning(f"Папка {upload_folder} не найдена.")
            return

        for file_name in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, file_name)
            if os.path.isfile(file_path):
                await upload_file(client, file_path, folder_id)

        # Обновляем статус клиента
        await sheet.update(f"C{rows.index(client_row) + 2}", "Загружено в Google Drive")
        logger.info(f"Файлы клиента {client_id} успешно загружены в Google Drive.")

    except Exception as e:
        logger.error(f"Ошибка при загрузке файлов клиента {client_id}: {e}", exc_info=True)
