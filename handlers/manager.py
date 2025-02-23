# handlers/manager.py
import asyncio
import os
from aiogram.filters import Command
from aiogram import Bot, Router, types
from aiogram.types import CallbackQuery, InputMediaDocument, FSInputFile
from core.utils.logging_utils import setup_logger
from core.google_sheets import get_google_sheet, update_client_status
from html import escape
from dotenv import load_dotenv
from core.utils.locales import get_text, load_user_languages  # Добавлен импорт мультиязычности

router = Router()
logger = setup_logger(__name__)

load_dotenv()
GOOGLE_SHEET_URL = os.getenv("GOOGLE_SHEET_URL")

def determine_sheet_name(message_text: str) -> str:
    """Определяет, в какой лист записывать данные"""
    return "Оптовые клиенты" if "опт" in message_text.lower() else "Розничные клиенты"

async def get_client_data(sheet_name: str, client_id: str):
    """Получает данные клиента из Google Sheets"""
    worksheet = await get_google_sheet(sheet_name)
    all_data = await worksheet.get_all_values()
    return next((row for row in all_data if str(row[1]).strip() == str(client_id).strip()), None)

async def get_valid_files(file_list: str):
    """Проверяет наличие файлов и разделяет их на найденные и отсутствующие"""
    if not file_list:
        return [], []

    files = [file.strip().replace("\\", "/") for file in file_list.split(",") if file.strip()]
    valid_files = [FSInputFile(f) for f in files if os.path.exists(f)]
    missing_files = [f for f in files if not os.path.exists(f)]
    return valid_files, missing_files

@router.callback_query(lambda c: c.data.startswith("details_"))
async def send_details(callback: CallbackQuery, bot: Bot):
    """Отправляет менеджеру всю информацию о клиенте + файлы и скрывает кнопки."""
    client_id = callback.data.split("_")[1]
    sheet_name = determine_sheet_name(callback.message.text)

    client_data = await get_client_data(sheet_name, client_id)
    if not client_data:
        await callback.message.answer(get_text("ru", "client_not_found"))  # Менеджер, скорее всего, русскоязычный
        await callback.answer(get_text("ru", "error_client_not_found"), show_alert=True)
        return

    status_updated = await update_client_status(sheet_name, client_id, "Просмотрено")
    files_column_index = 3 if sheet_name == "Оптовые клиенты" else 4

    details_msg = (
        f"📋 <b>{get_text('ru', 'order_details')}:</b>\n"
        f"👤 <b>{get_text('ru', 'client')}:</b> {escape(client_data[0])}\n"
        f"📌 <b>{get_text('ru', 'category')}:</b> {escape(client_data[2])}\n"
        f"📂 <b>{get_text('ru', 'files')}:</b> {escape(client_data[files_column_index])}\n"
        f"🗒 <b>{get_text('ru', 'comment')}:</b> {escape(client_data[files_column_index + 1])}\n"
        f"📲 <b>{get_text('ru', 'contacts')}:</b> {escape(client_data[files_column_index + 2])}\n"
        f"📅 <b>{get_text('ru', 'date')}:</b> {escape(client_data[files_column_index + 3])}\n"
        f"📁 <b>{get_text('ru', 'file_count')}:</b> {escape(client_data[files_column_index + 4])}\n"
        f"📝 <b>{get_text('ru', 'status')}:</b> {'✅ ' + get_text('ru', 'updated') if status_updated else '⚠ ' + get_text('ru', 'error')}"
    )

    await callback.message.edit_text(details_msg, parse_mode="HTML")

    # Обрабатываем файлы
    valid_files, missing_files = await get_valid_files(client_data[files_column_index])

    if missing_files:
        logger.warning(f"⚠ {get_text('ru', 'missing_files')}: {missing_files}")
        await callback.message.answer(f"⚠ {get_text('ru', 'missing_files')}:\n" + "\n".join(missing_files))

    # Отправляем файлы по 10 за раз
    for i in range(0, len(valid_files), 10):
        batch = valid_files[i:i + 10]
        media_group = [InputMediaDocument(media=file) for file in batch]

        try:
            await bot.send_media_group(callback.message.chat.id, media_group)
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"{get_text('ru', 'error_sending_files')}: {e}")
            await callback.message.answer(get_text('ru', "error_sending_files"))

    await callback.answer(get_text("ru", "info_sent_to_manager"))

@router.message(Command("sheet"))
async def send_sheet_link(message: types.Message):
    """Отправляет ссылку на Google Sheets."""
    await message.answer(f"📄 {get_text('ru', 'sheet_link')}: {GOOGLE_SHEET_URL}", reply_markup=types.ReplyKeyboardRemove())
