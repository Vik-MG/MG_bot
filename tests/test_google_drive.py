# tests/test_google_drive.py
import asyncio
from core.google_drive import get_authenticated_client
from aiogoogle import Aiogoogle

async def check_drive_access():
    """Проверяет доступ сервисного аккаунта к Google Drive"""
    try:
        client = await get_authenticated_client()
        async with client as g_client:
            drive_service = await g_client.discover("drive", "v3")
            response = await g_client.as_service_account(
                drive_service.files.list(q="'root' in parents", fields="files(id, name)", pageSize=5)
            )
            files = response.get("files", [])
            if files:
                print("✅ Сервисный аккаунт видит файлы в Google Drive:")
                for file in files:
                    print(f"📂 {file['name']} (ID: {file['id']})")
            else:
                print("⚠ Сервисный аккаунт не видит файлы в Google Drive. Проверь права доступа!")
    except Exception as e:
        print(f"❌ Ошибка доступа к Google Drive: {e}")

asyncio.run(check_drive_access())

async def list_drive_files():
    """Проверяет доступ сервисного аккаунта и выводит список файлов"""
    try:
        client = await get_authenticated_client()
        async with client as g_client:
            drive_service = await g_client.discover("drive", "v3")
            response = await g_client.as_service_account(
                drive_service.files.list(fields="files(id, name)", pageSize=10)
            )
            files = response.get("files", [])
            if files:
                print("✅ Сервисный аккаунт видит файлы в Google Drive:")
                for file in files:
                    print(f"📂 {file['name']} (ID: {file['id']})")
            else:
                print("⚠ В Google Drive нет доступных файлов.")
    except Exception as e:
        print(f"❌ Ошибка при запросе списка файлов: {e}")

if __name__ == "__main__":
    asyncio.run(list_drive_files())