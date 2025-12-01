# handlers/contacts.py

from aiogram import Router, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram import F
from core.google_sheets import initialize_google_sheet, get_google_sheet
from core.utils.logging_utils import setup_logger
from core.states import Form
from datetime import datetime
import os
import asyncio
from dotenv import load_dotenv
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from core.utils.locales import get_text, load_user_languages

import re  # ДОБАВЛЕНО: для проверки корректного номера

# Загрузка переменных окружения
load_dotenv()
MANAGER_ID = os.getenv("MANAGER_ID")

logger = setup_logger(__name__)
router = Router()


def get_actual_files(user_id: int) -> list[str]:
    """Возвращает список всех файлов в папке пользователя."""
    user_folder = os.path.join("uploads", str(user_id))
    if not os.path.exists(user_folder):
        return []

    return sorted([
        os.path.join(user_folder, f) for f in os.listdir(user_folder)
        if os.path.isfile(os.path.join(user_folder, f))
    ])


# НОВОЕ: функция проверки вручную введенного номера
def is_valid_phone(text: str) -> bool:
    cleaned = re.sub(r"[^\d+]", "", text)  # убираем лишние символы
    return bool(re.match(r"^\+?\d{7,20}$", cleaned))


# ---------------------- ОСНОВНОЙ ОБРАБОТЧИК ----------------------
# Раньше было: @router.message(Form.contacts) (принимал всё)
@router.message(Form.contacts, F.contact | F.text)  # НОВОЕ УСЛОВИЕ: обработчик принимает и контакт, и текст
async def get_contacts(message: types.Message, state: FSMContext, bot: Bot):
    """Получение и сохранение контакта."""

    user_id = message.from_user.id
    data = await state.get_data()
    lang = data.get("language", load_user_languages().get(str(user_id), "ru"))

    # ------------------- ЛОГИКА 1: Контакт через кнопку -------------------
    if message.contact:  # НОВОЕ: приоритет контакту
        contacts = message.contact.phone_number
        logger.info(f"Получен номер через кнопку: {contacts}")

    # ------------------- ЛОГИКА 2: Текст → проверка номера -------------------
    else:
        # contacts = message.text.strip()  # СТАРАЯ ЛОГИКА - теперь контролируем
        user_input = message.text.strip()

        if is_valid_phone(user_input):
            contacts = user_input
            logger.info(f"Принят корректный номер, введённый вручную: {contacts}")
        else:
            # ------------------- НЕВЕРНЫЙ ВВОД → предлагаем кнопку -------------------
            logger.warning(f"Некорректный ввод номера: {user_input}")

            keyboard = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)]],
                resize_keyboard=True
            )

            await message.answer(
                "Похоже, номер введён неверно.\n"
                "Чтобы не ошибиться — нажмите кнопку ниже.",
                reply_markup=keyboard
            )
            return  # ВАЖНО: НЕ продолжаем, пока не будет нормального ввода


    # ------------------- ЕСЛИ МЫ ЗДЕСЬ — номер валиден -------------------
    await state.update_data(contacts=contacts)

    # ЗАГРУЗКА ФАЙЛОВ, ОБРАБОТКА СТАРОГО КОДА (Без изменений)
    await asyncio.sleep(2)
    actual_files = get_actual_files(user_id)

    file_list = data.get("file_list", "")
    if isinstance(file_list, str) and file_list:
        file_list = file_list.split(",")
    elif not isinstance(file_list, list):
        file_list = []

    file_list.extend(actual_files)
    file_list = sorted(set(file_list))

    await state.update_data(file_list=",".join(file_list))
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    client_type = data.get("client_type", "").lower()
    sheet_name = "Оптовые клиенты" if client_type == "оптовый" else "Розничные клиенты"

    if client_type == "оптовый":
        headers = ["Имя клиента", "ID", "Проект", "Файлы", "Комментарий", "Контакты", "Дата", "Кол-во", "Статус"]
        row = [
            data.get("name", ""), user_id, data.get("opt_project", ""),
            ", ".join(file_list), data.get("combined_comment", "").strip(),
            contacts, timestamp, len(file_list), "Новый"
        ]
    else:
        headers = ["Имя клиента", "ID", "Проект", "Кладбище", "Файлы", "Комментарий", "Контакты", "Дата", "Кол-во", "Статус"]
        row = [
            data.get("name", ""), user_id, data.get("item_interest", ""), data.get("cemetery", ""),
            ", ".join(file_list), data.get("combined_comment", "").strip(),
            contacts, timestamp, len(file_list), "Новый"
        ]

    try:
        worksheet = await get_google_sheet(sheet_name)
        await initialize_google_sheet(worksheet, headers)
        await worksheet.append_row(row)

        await message.answer(get_text(lang, "thank_you"))

        if MANAGER_ID:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📋 Подробнее", callback_data=f"details_{user_id}")]
            ])
            notification = (
                f"📝 *{get_text(lang, 'new_order')}*\n"
                f"📅 *{get_text(lang, 'date')}:* {timestamp}\n\n"
                f"👤 *{get_text(lang, 'client')}:* {data.get('name', 'Unknown')}\n"
                f"📌 *{get_text(lang, 'category')}:* {client_type.capitalize()}\n"
                f"🗒 *{get_text(lang, 'comment')}:* {data.get('combined_comment', '').strip()}\n"
                f"📂 *{get_text(lang, 'files')}:* {len(file_list)}"
            )
            await bot.send_message(MANAGER_ID, notification, reply_markup=keyboard, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Ошибка записи в Google Sheets: {e}")
        await message.answer(get_text(lang, "error_saving_data"))

    finally:
        await state.clear()



