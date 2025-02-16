# core.google_drive.py
import os
import json
import asyncio
from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds
from core.config import CREDENTIALS_FILE_DRIVE, GOOGLE_API_SCOPE
from core.google_sheets import get_google_sheet
from core.utils.logging_utils import setup_logger

logger = setup_logger(__name__)

async def get_authenticated_client():
    """Аутентификация в Google API через aiogoogle."""
    with open(CREDENTIALS_FILE_DRIVE, "r", encoding="utf-8") as f:
        credentials_data = json.load(f)
    
    creds = ServiceAccountCreds(scopes=GOOGLE_API_SCOPE, **credentials_data)
    return Aiogoogle(service_account_creds=creds)

async def create_drive_folder(client: Aiogoogle, folder_name: str, parent_id: str) -> str:
    """Создаёт папку в Google Drive."""
    drive_service = await client.discover("drive", "v3")
    response = await client.as_service_account(
        drive_service.files.create(
            json={"name": folder_name, "mimeType": "application/vnd.google-apps.folder", "parents": [parent_id]},
            fields="id"
        )
    )
    return response["id"]

async def upload_file(client: Aiogoogle, file_path: str, folder_id: str) -> str:
    """Загружает файл в Google Drive."""
    drive_service = await client.discover("drive", "v3")
    metadata = {"name": os.path.basename(file_path), "parents": [folder_id]}
    
    with open(file_path, "rb") as f:
        file_content = f.read()
    
    response = await client.as_service_account(
        drive_service.files.create(
            json=metadata,
            media_body=file_content,
            fields="id"
        )
    )
    return response["id"]

async def upload_all_new_clients():
    """Загружает файлы всех клиентов со статусом 'Новый' в Google Drive."""
    sheet = await get_google_sheet("Розничные клиенты")
    data = await sheet.get_all_values()
    headers, *rows = data
    status_index = headers.index("Статус")
    id_index = headers.index("ID")
    
    async with await get_authenticated_client() as client:
        parent_folder_id = "1nCoOjylySTUeu9_wuBHkL6wkJ4ziDtKy"
        
        for row in rows:
            if row[status_index] == "Новый":
                client_id = row[id_index]
                client_folder = os.path.join("uploads", str(client_id))
                
                if os.path.exists(client_folder):
                    folder_id = await create_drive_folder(client, str(client_id), parent_folder_id)
                    
                    for file_name in os.listdir(client_folder):
                        file_path = os.path.join(client_folder, file_name)
                        if os.path.isfile(file_path):
                            await upload_file(client, file_path, folder_id)
                    
                    row_num = rows.index(row) + 2
                    await sheet.update(f"{chr(65 + status_index)}{row_num}", [["Загружено в Google Drive"]])
                    logger.info(f"Файлы клиента {client_id} загружены.")
                else:
                    logger.warning(f"Папка клиента {client_id} не найдена.")

if __name__ == "__main__":
    asyncio.run(upload_all_new_clients())
