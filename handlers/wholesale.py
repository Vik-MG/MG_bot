# handlers/wholesale.py
"""
Обработчики для взаимодействия с оптовыми клиентами.
- Выбор типа проекта.
- Обработка деталей проекта.
"""

from aiogram import Router, Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import ContentType, InlineKeyboardMarkup, InlineKeyboardButton
from handlers.common import process_input
from core.states import Form
from core.utils.logging_utils import setup_logger

# Настройка логгера
logger = setup_logger(__name__)

# Создаём Router
router = Router()

@router.callback_query(StateFilter(Form.opt_project), lambda c: c.data in ["Камнеобработчик", "Смежная сфера"])
async def get_opt_project(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка выбора типа проекта для оптовых клиентов."""
    try:
        opt_project = callback_query.data
        await state.update_data(opt_project=opt_project)
        logger.info(f"Выбран тип проекта: {opt_project} (пользователь {callback_query.from_user.id}).")

        await callback_query.message.answer(
            "Есть ли конкретный проект? Опишите его или отправьте файл с проектом."
        )
        await state.set_state(Form.wholesale_details)
    except Exception as e:
        logger.error(f"Ошибка при выборе типа проекта: {e}", exc_info=True)
        await callback_query.message.answer("Произошла ошибка. Попробуйте снова.")

@router.message(StateFilter(Form.wholesale_details), lambda message: message.content_type in [ContentType.TEXT, ContentType.PHOTO, ContentType.DOCUMENT])
async def get_wholesale_details(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка деталей для оптовых клиентов."""
    try:
        logger.info(f"Получены детали от пользователя {message.from_user.id}.")
        await process_input(message, state, bot=bot)
    except Exception as e:
        logger.error(f"Ошибка при обработке деталей: {e}", exc_info=True)
        await message.answer("Произошла ошибка. Попробуйте снова.")
