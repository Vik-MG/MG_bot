# handlers/wholesale.py
"""
Обработчики для взаимодействия с оптовыми клиентами.
- Выбор типа проекта.
- Обработка деталей проекта.
"""

from aiogram import Router, Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import ContentType
from handlers.common import process_input
from core.states import Form
from core.utils.logging_utils import setup_logger
from core.utils.locales import get_text, load_user_languages  # Добавлен импорт мультиязычности

# Настройка логгера
logger = setup_logger(__name__)

# Создаём Router
router = Router()

@router.callback_query(StateFilter(Form.opt_project), lambda c: c.data in ["Камнеобработчик", "Смежная сфера"])
async def get_opt_project(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка выбора типа проекта для оптовых клиентов."""
    try:
        user_id = callback_query.from_user.id
        opt_project = callback_query.data
        await state.update_data(opt_project=opt_project)

        # Определение языка пользователя
        data = await state.get_data()
        lang = data.get("language", load_user_languages().get(str(user_id), "ru"))

        logger.info(f"Выбран тип проекта: {opt_project} (пользователь {user_id}).")

        await callback_query.message.answer(get_text(lang, "describe_project"))
        await state.set_state(Form.wholesale_details)
    except Exception as e:
        logger.error(f"Ошибка при выборе типа проекта: {e}", exc_info=True)
        await callback_query.message.answer(get_text(lang, "error_occurred"))

@router.message(StateFilter(Form.wholesale_details), lambda message: message.content_type in [ContentType.TEXT, ContentType.PHOTO, ContentType.DOCUMENT])
async def get_wholesale_details(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка деталей для оптовых клиентов."""
    try:
        user_id = message.from_user.id

        # Определение языка пользователя
        data = await state.get_data()
        lang = data.get("language", load_user_languages().get(str(user_id), "ru"))

        logger.info(f"Получены детали от пользователя {user_id}.")
        await process_input(message, state, bot=bot)
    except Exception as e:
        logger.error(f"Ошибка при обработке деталей: {e}", exc_info=True)
        await message.answer(get_text(lang, "error_occurred"))
