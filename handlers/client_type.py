# handlers/client_type.py
from aiogram import Router, Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.states import Form
from core.utils.logging_utils import setup_logger
from core.utils.locales import get_text, load_user_languages  # Добавлен импорт мультиязычности

# Настройка логгера
logger = setup_logger(__name__)

# Создаем Router
router = Router()

@router.message(StateFilter(Form.client_type))
async def get_client_type(message: types.Message, state: FSMContext):
    """Обработка ввода имени клиента и предложение выбора типа."""
    try:
        user_id = message.from_user.id
        name = message.text
        await state.update_data(name=name)

        # Получаем язык пользователя
        data = await state.get_data()
        lang = data.get("language", load_user_languages().get(str(user_id), "ru"))

        logger.info(f"Получено имя клиента: {name}")

        # Клавиатура выбора типа клиента
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=get_text(lang, "wholesale"), callback_data="Оптовый")],
                [InlineKeyboardButton(text=get_text(lang, "retail"), callback_data="Розничный")]
            ]
        )

        await message.answer(
            get_text(lang, "client_greeting").format(name=name),
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Ошибка в обработке имени клиента: {e}", exc_info=True)
        await message.answer(get_text(lang, "error_name_input"))

@router.callback_query(StateFilter(Form.client_type), lambda c: c.data in ["Оптовый", "Розничный"])
async def process_client_type(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка выбора типа клиента."""
    try:
        user_id = callback_query.from_user.id
        client_type = callback_query.data
        await state.update_data(client_type=client_type)

        # Получаем язык пользователя
        data = await state.get_data()
        lang = data.get("language", load_user_languages().get(str(user_id), "ru"))

        logger.info(f"Тип клиента выбран: {client_type}")

        if client_type == "Оптовый":
            # Клавиатура для оптовых клиентов
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=get_text(lang, "stone_processing"), callback_data="Камнеобработчик")],
                    [InlineKeyboardButton(text=get_text(lang, "related_industry"), callback_data="Смежная сфера")]
                ]
            )

            await callback_query.message.answer(
                get_text(lang, "wholesale_question"),
                reply_markup=keyboard
            )
            await state.set_state(Form.opt_project)  # Переход к следующему состоянию
        else:
            # Клавиатура для розничных клиентов
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text=get_text(lang, "monuments"), callback_data="Памятники")],
                    [InlineKeyboardButton(text=get_text(lang, "other_products"), callback_data="Другие изделия")]
                ]
            )

            await callback_query.message.answer(
                get_text(lang, "retail_question"),
                reply_markup=keyboard
            )
            await state.set_state(Form.item_interest)  # Переход к следующему состоянию
    except Exception as e:
        logger.error(f"Ошибка в обработке выбора типа клиента: {e}", exc_info=True)
        await callback_query.message.answer(get_text(lang, "error_client_type"))
