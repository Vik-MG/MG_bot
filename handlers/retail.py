# handlers/retail.py
from aiogram import Router, Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import ContentType
from handlers.common import process_input
from core.states import Form
from core.utils.logging_utils import setup_logger
from core.utils.locales import get_text, load_user_languages  # Добавлен импорт мультиязычности

logger = setup_logger(__name__)

router = Router()

@router.callback_query(StateFilter(Form.item_interest), lambda c: c.data in ["Памятники", "Другие изделия"])
async def get_item_interest(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка выбора интереса для розничных клиентов."""
    try:
        user_id = callback_query.from_user.id
        item_interest = callback_query.data
        await state.update_data(item_interest=item_interest)

        # Определение языка пользователя
        data = await state.get_data()
        lang = data.get("language", load_user_languages().get(str(user_id), "ru"))

        logger.info(f"Выбран интерес: {item_interest} (пользователь {user_id}).")

        if item_interest == "Памятники":
            await callback_query.message.answer(get_text(lang, "cemetery_question"))
            await state.set_state(Form.cemetery)
        else:
            await callback_query.message.answer(get_text(lang, "describe_item"))
            await state.set_state(Form.item_details)
    except Exception as e:
        logger.error(f"Ошибка при выборе интереса: {e}", exc_info=True)
        await callback_query.message.answer(get_text(lang, "error_occurred"))

@router.message(StateFilter(Form.cemetery))
async def get_cemetery(message: types.Message, state: FSMContext):
    """Обработка ввода информации о кладбище."""
    try:
        user_id = message.from_user.id
        cemetery = message.text.strip()
        await state.update_data(cemetery=cemetery)

        # Определение языка пользователя
        data = await state.get_data()
        lang = data.get("language", load_user_languages().get(str(user_id), "ru"))

        logger.info(f"Введено кладбище: {cemetery} (пользователь {user_id}).")

        await message.answer(get_text(lang, "describe_monument"))
        await state.set_state(Form.monument)
    except Exception as e:
        logger.error(f"Ошибка при вводе информации о кладбище: {e}", exc_info=True)
        await message.answer(get_text(lang, "error_occurred"))

@router.message(StateFilter(Form.monument), lambda message: message.content_type in [ContentType.TEXT, ContentType.PHOTO, ContentType.DOCUMENT])
async def get_monument_details(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка деталей памятника."""
    try:
        user_id = message.from_user.id

        # Определение языка пользователя
        data = await state.get_data()
        lang = data.get("language", load_user_languages().get(str(user_id), "ru"))

        logger.info(f"Получены данные о памятнике от пользователя {user_id}.")
        await process_input(message, state, bot=bot)
    except Exception as e:
        logger.error(f"Ошибка при обработке деталей памятника: {e}", exc_info=True)
        await message.answer(get_text(lang, "error_occurred"))

@router.message(StateFilter(Form.item_details), lambda message: message.content_type in [ContentType.TEXT, ContentType.PHOTO, ContentType.DOCUMENT])
async def get_item_details(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка деталей для розничных клиентов."""
    try:
        user_id = message.from_user.id

        # Определение языка пользователя
        data = await state.get_data()
        lang = data.get("language", load_user_languages().get(str(user_id), "ru"))

        logger.info(f"Получены данные о предмете от пользователя {user_id}.")
        await process_input(message, state, bot=bot)
    except Exception as e:
        logger.error(f"Ошибка при обработке деталей предмета: {e}", exc_info=True)
        await message.answer(get_text(lang, "error_occurred"))
