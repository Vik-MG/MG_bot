# handlers/contacts.py 
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from core.google_sheets import initialize_google_sheet, get_google_sheet
from core.utils.logging_utils import setup_logger
from core.states import Form
from datetime import datetime
from aiogram import Bot
import os
import asyncio
from dotenv import load_dotenv
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Загрузка переменных окружения
load_dotenv()
MANAGER_ID = os.getenv("MANAGER_ID")

# Настройка логгера
logger = setup_logger(__name__)

# Создаём Router
router = Router()

def get_actual_files(user_id: int) -> list[str]:
    """Возвращает список всех файлов в папке пользователя."""
    user_folder = os.path.join("uploads", str(user_id))
    return sorted([
        os.path.join(user_folder, f) for f in os.listdir(user_folder)
        if os.path.isfile(os.path.join(user_folder, f))
    ])

@router.message(Form.contacts)
async def get_contacts(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ввода контактов и сохранение данных в Google Sheets."""
    try:
        logger.info(f"Начало обработки контактов. Пользователь: {message.from_user.id}, Контакты: {message.text}")
        contacts = message.text

        await state.update_data(contacts=contacts)

        # Получаем все данные из FSM
        data = await state.get_data()
        logger.debug(f"Полученные данные FSM перед обновлением: {data}")

        # Загружаем актуальные файлы
        await asyncio.sleep(2)  # Ожидаем запись файлов
        actual_files = get_actual_files(message.from_user.id)

        # Обновляем данные FSM один раз
        await state.update_data(file_list=",".join(actual_files))

        # Проверяем количество файлов
        saved_files_count = len(actual_files)
        if saved_files_count != len(actual_files):
            logger.warning(f"⚠️ Несоответствие файлов! В папке {saved_files_count}, в FSM {len(actual_files)}.")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        def prepare_data_and_headers(client_type: str):
            """Формирует заголовки и строки для Google Sheets."""
            if client_type == "оптовый":
                return "Оптовые клиенты", ["Имя клиента", "ID", "Проект", "Файлы", "Комментарий", "Контакты", "Дата", "Кол-во", "Статус"], [
                    data.get("name", ""),
                    message.from_user.id,
                    data.get("opt_project", ""),
                    ", ".join(actual_files),
                    data.get("combined_comment", "").strip(),
                    contacts,
                    timestamp,
                    saved_files_count,
                    "Новый"
                ]
            elif client_type == "розничный":
                return "Розничные клиенты", ["Имя клиента", "ID", "Проект", "Кладбище", "Файлы", "Комментарий", "Контакты", "Дата", "Кол-во", "Статус"], [
                    data.get("name", ""),
                    message.from_user.id,
                    data.get("item_interest", ""),
                    data.get("cemetery", ""),
                    ", ".join(actual_files),
                    data.get("combined_comment", "").strip(),
                    contacts,
                    timestamp,
                    saved_files_count,
                    "Новый"
                ]
            else:
                logger.error("❌ Неизвестный тип клиента.")
                return None, None, None

        # Определяем тип клиента
        client_type = data.get("client_type", "").lower()
        sheet_name, headers, row = prepare_data_and_headers(client_type)

        if not sheet_name:
            await message.answer("⚠ Ошибка: тип клиента не указан. Обратитесь к администратору.")
            return

        # Запись в Google Sheets
        try:
            worksheet = await get_google_sheet(sheet_name)
            logger.debug(f"Лист {sheet_name} успешно получен.")

            await initialize_google_sheet(worksheet, headers)
            logger.debug(f"Заголовки {headers} успешно инициализированы.")

            if row:
                await worksheet.append_row(row)
                logger.info(f"✅ Данные успешно записаны: {row}")
            else:
                logger.error("❌ Ошибка: пустая строка для записи.")
                await message.answer("⚠ Ошибка записи данных. Попробуйте позже.")
                return

            await message.answer("Спасибо! Ваш запрос сохранён. Мы свяжемся с вами в ближайшее время.")

            # Уведомление менеджера
            if MANAGER_ID:
                client_category = "Оптовый" if client_type == "оптовый" else "Розничный"
                client_interest = data.get("opt_project", "Камнеобработчик") if client_type == "оптовый" else data.get("item_interest", "Памятники/Другие изделия")

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📞 Связаться", callback_data=f"contact_{message.from_user.id}")],
                    [InlineKeyboardButton(text="📋 Подробнее", callback_data=f"details_{message.from_user.id}")]
                ])

                notification = (f"📝 *Новый заказ!*\n"
                                f"📅 *Дата:* {timestamp}\n"
                                f"👤 *Клиент:* {data.get('name', 'Unknown')}\n"
                                f"📌 *Категория:* {client_category}\n"
                                f"🔍 *Интерес:* {client_interest}\n"
                                f"🗒 *Комментарий:* {data.get('combined_comment', '').strip()}\n"
                                f"📂 *Файлы:* {saved_files_count}")

                await bot.send_message(MANAGER_ID, notification, reply_markup=keyboard, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"❌ Ошибка записи в Google Sheets: {e}")
            await message.answer("⚠ Ошибка при записи данных. Попробуйте позже.")
    finally:
        await state.clear()
