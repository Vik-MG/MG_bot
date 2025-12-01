# handlers/contacts.py
from aiogram import Router, types
from aiogram import Bot
from aiogram import F  # ДОБАВЛЕНО: фильтр F для обработки только контактов
from aiogram.fsm.context import FSMContext
from core.google_sheets import initialize_google_sheet, get_google_sheet
from core.utils.logging_utils import setup_logger
from core.states import Form
from datetime import datetime
import os
import asyncio
from dotenv import load_dotenv
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton  # СТАРАЯ СТРОКА ИМПОРТА
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton  # НОВОЕ: добавлены ReplyKeyboardMarkup, KeyboardButton
from core.utils.locales import get_text, load_user_languages  # Добавлен импорт мультиязычности

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
    if not os.path.exists(user_folder):
        return []

    return sorted([
        os.path.join(user_folder, f) for f in os.listdir(user_folder)
        if os.path.isfile(os.path.join(user_folder, f))
    ])


# @router.message(Form.contacts)  # СТАРАЯ ВЕРСИЯ: принимала любой текст как "контакты"
@router.message(Form.contacts, F.contact)  # НОВАЯ ВЕРСИЯ: обработчик срабатывает ТОЛЬКО на отправку контакта
async def get_contacts(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ввода контактов и сохранение данных в Google Sheets."""
    try:
        user_id = message.from_user.id
        data = await state.get_data()
        lang = data.get("language", load_user_languages().get(str(user_id), "ru"))  # Получаем язык пользователя

        # contacts = message.text.strip()  # СТАРАЯ ВЕРСИЯ: любой введённый текст считался контактами
        contacts = message.contact.phone_number  # НОВАЯ ВЕРСИЯ: берём номер из контакта Telegram

        logger.info(f"Начало обработки контактов. Пользователь: {user_id}, Контакты: {contacts}")
        await state.update_data(contacts=contacts)

        # Загружаем актуальные файлы
        await asyncio.sleep(2)
        actual_files = get_actual_files(user_id)

        # Обновляем данные FSM
        file_list = data.get("file_list", "")
        if isinstance(file_list, str) and file_list:
            file_list = file_list.split(",")
        elif not isinstance(file_list, list):
            file_list = []

        file_list.extend(actual_files)
        file_list = sorted(set(file_list))  # Убираем дубликаты

        await state.update_data(file_list=",".join(file_list))
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Определяем тип клиента
        client_type = data.get("client_type", "").lower()
        sheet_name = "Оптовые клиенты" if client_type == "оптовый" else "Розничные клиенты"

        # Формируем данные в зависимости от типа клиента
        if client_type == "оптовый":
            headers = ["Имя клиента", "ID", "Проект", "Файлы", "Комментарий", "Контакты", "Дата", "Кол-во", "Статус"]
            row = [
                data.get("name", ""),
                user_id,
                data.get("opt_project", ""),
                ", ".join(file_list),
                data.get("combined_comment", "").strip(),
                contacts,
                timestamp,
                len(file_list),
                "Новый"
            ]
        else:  # Розничный клиент
            headers = ["Имя клиента", "ID", "Проект", "Кладбище", "Файлы", "Комментарий", "Контакты", "Дата", "Кол-во", "Статус"]
            row = [
                data.get("name", ""),
                user_id,
                data.get("item_interest", ""),
                data.get("cemetery", ""),
                ", ".join(file_list),
                data.get("combined_comment", "").strip(),
                contacts,
                timestamp,
                len(file_list),
                "Новый"
            ]

        # Запись в Google Sheets
        try:
            worksheet = await get_google_sheet(sheet_name)
            await initialize_google_sheet(worksheet, headers)
            await worksheet.append_row(row)
            logger.info(f"✅ Данные успешно записаны: {row}")
            await message.answer(get_text(lang, "thank_you"))  # Локализованное сообщение

            # Уведомление менеджера
            if MANAGER_ID:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📋 Подробнее", callback_data=f"details_{user_id}")]
                ])
                notification = (f"📝 *{get_text(lang, 'new_order')}*\n"
                                f"📅 *{get_text(lang, 'date')}:* {timestamp}\n\n"
                                f"👤 *{get_text(lang, 'client')}:* {data.get('name', 'Unknown')}\n"
                                f"📌 *{get_text(lang, 'category')}:* {client_type.capitalize()}\n"
                                f"🗒 *{get_text(lang, 'comment')}:* {data.get('combined_comment', '').strip()}\n"
                                f"📂 *{get_text(lang, 'files')}:* {len(file_list)}")
                await bot.send_message(MANAGER_ID, notification, reply_markup=keyboard, parse_mode="Markdown")

        except Exception as e:
            logger.error(f"❌ Ошибка записи в Google Sheets: {e}")
            await message.answer(get_text(lang, "error_saving_data"))

    except Exception as e:
        logger.error(f"❌ Ошибка при обработке контактов: {e}")
        await message.answer(get_text(lang, "error_saving_data"))

    finally:
        await state.clear()


# НОВЫЙ ОБРАБОТЧИК:
# Не даёт пользователю "проскочить" дальше, если он пишет текст вместо отправки контакта
@router.message(Form.contacts)
async def ask_contact_strict(message: types.Message):
    """
    Пользователь находится в состоянии Form.contacts, но прислал не контакт.
    Повторно просим отправить номер телефона через кнопку с request_contact.
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(
        "Для продолжения нужно отправить номер телефона.\n"
        "Пожалуйста, нажмите кнопку ниже и поделитесь контактом.",
        reply_markup=keyboard
    )

