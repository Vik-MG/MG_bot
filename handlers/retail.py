# handlers/retail.py
from aiogram import Router, Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import ContentType  # Используем ContentType вместо ContentTypesFilter
from handlers.common import process_input
from core.states import Form
from core.utils.logging_utils import setup_logger

# Настройка логгера
logger = setup_logger(__name__)

# Создаём Router
router = Router()

@router.callback_query(lambda c: c.data in ["Памятники", "Другие изделия"], StateFilter(Form.item_interest))
async def get_item_interest(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка выбора интереса для розничных клиентов."""
    try:
        item_interest = callback_query.data
        await state.update_data(item_interest=item_interest)
        logger.info(f"Выбран интерес: {item_interest} (пользователь {callback_query.from_user.id}).")

        if item_interest == "Памятники":
            await callback_query.message.answer(
                "Сочувствую Вашей утрате. Подскажите пожалуйста, на каком кладбище находится захоронение?"
            )
            await state.set_state(Form.cemetery)
        else:
            await callback_query.message.answer(
                "Опишите, что именно вы хотите. Вы можете прислать фото, проект или текстовое описание."
            )
            await state.set_state(Form.item_details)
    except Exception as e:
        logger.error(f"Ошибка при выборе интереса: {e}", exc_info=True)
        await callback_query.message.answer("Произошла ошибка. Попробуйте снова.")

@router.message(StateFilter(Form.cemetery))
async def get_cemetery(message: types.Message, state: FSMContext):
    """Обработка ввода информации о кладбище."""
    try:
        cemetery = message.text
        await state.update_data(cemetery=cemetery)
        logger.info(f"Введено кладбище: {cemetery} (пользователь {message.from_user.id}).")

        await message.answer(
            "Опишите, какой памятник вы хотите. Вы можете отправить фото, проект или текстовое описание."
        )
        await state.set_state(Form.monument)
    except Exception as e:
        logger.error(f"Ошибка при вводе информации о кладбище: {e}", exc_info=True)
        await message.answer("Произошла ошибка. Попробуйте снова.")

@router.message(StateFilter(Form.monument), lambda message: message.content_type in [ContentType.TEXT, ContentType.PHOTO, ContentType.DOCUMENT])
async def get_monument_details(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка деталей памятника."""
    try:
        logger.info(f"Получены данные о памятнике от пользователя {message.from_user.id}.")
        await process_input(message, state, bot=bot)
    except Exception as e:
        logger.error(f"Ошибка при обработке деталей памятника: {e}", exc_info=True)
        await message.answer("Произошла ошибка. Попробуйте снова.")

@router.message(StateFilter(Form.item_details), lambda message: message.content_type in [ContentType.TEXT, ContentType.PHOTO, ContentType.DOCUMENT])
async def get_item_details(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка деталей для розничных клиентов."""
    try:
        logger.info(f"Получены данные о предмете от пользователя {message.from_user.id}.")
        await process_input(message, state, bot=bot)
    except Exception as e:
        logger.error(f"Ошибка при обработке деталей предмета: {e}", exc_info=True)
        await message.answer("Произошла ошибка. Попробуйте снова.")
