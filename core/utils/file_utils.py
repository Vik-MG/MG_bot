# core/utils/file_utils.py
import os
from aiogram import Bot, types
from datetime import datetime
from core.utils.logging_utils import setup_logger

logger = setup_logger(__name__)

async def save_file(message: types.Message, bot: Bot, upload_dir: str = "uploads") -> str:
    """
    Сохраняет фотографию или документ, отправленный пользователем, в локальной директории.

    Args:
        message (types.Message): Telegram message object.
        bot (Bot): Экземпляр aiogram.Bot.
        upload_dir (str): Базовая директория для сохранения загруженных файлов.

    Returns:
        str: Путь к сохранённому файлу.
    """
    user_id = message.from_user.id
    user_folder = os.path.join(upload_dir, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    logger.info(f"Создана директория для пользователя {user_id} в {user_folder}.")

    if message.photo:
        # Save the highest-quality photo
        file = message.photo[-1]
        file_name = f"photo_{file.file_id}.jpg"
        file_path = os.path.join(user_folder, file_name)
    elif message.document:
        # Save the document
        file = message.document
        file_name = file.file_name or f"document_{file.file_id}"
        file_path = os.path.join(user_folder, file_name)
    else:
        logger.warning(f"Сообщение от пользователя {user_id} не содержит поддерживаемых медиа.")
        raise ValueError("Сообщение не содержит поддерживаемых медиафайлов.")

    try:
        file_info = await bot.get_file(file.file_id)
        await bot.download_file(file_info.file_path, destination=file_path)
        logger.info(f"Файл {file_name} успешно сохранён в {file_path}.")
        return file_path
    except Exception as e:
        logger.error(f"Ошибка сохранения файла {file_name}: {e}", exc_info=True)
        raise
