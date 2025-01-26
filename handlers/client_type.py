# handlers/client_type.py
from aiogram import Router, Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.states import Form
from core.utils.logging_utils import setup_logger

# Настройка логгера
logger = setup_logger(__name__)

# Создаем Router
router = Router()

@router.message(StateFilter(Form.client_type))
async def get_client_type(message: types.Message, state: FSMContext):
    """Обработка ввода имени клиента и предложение выбора типа."""
    try:
        name = message.text
        await state.update_data(name=name)
        logger.info(f"Получено имя клиента: {name}")

        # Клавиатура выбора типа клиента
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Оптовый", callback_data="Оптовый")],
                [InlineKeyboardButton(text="Розничный", callback_data="Розничный")]
            ]
        )

        await message.answer(
            f"Приятно познакомиться, {name}. Вы клиент оптовый или розничный?",
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Ошибка в обработке имени клиента: {e}", exc_info=True)
        await message.answer("Произошла ошибка при вводе имени. Попробуйте снова.")

@router.callback_query(StateFilter(Form.client_type), lambda c: c.data in ["Оптовый", "Розничный"])
async def process_client_type(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка выбора типа клиента."""
    try:
        client_type = callback_query.data
        await state.update_data(client_type=client_type)
        logger.info(f"Тип клиента выбран: {client_type}")

        if client_type == "Оптовый":
            # Клавиатура для оптовых клиентов
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Камнеобработчик", callback_data="Камнеобработчик")],
                    [InlineKeyboardButton(text="Смежная сфера", callback_data="Смежная сфера")]
                ]
            )

            await callback_query.message.answer(
                "Вы занимаетесь камнеобработкой или работаете в смежной сфере?",
                reply_markup=keyboard
            )
            await state.set_state(Form.opt_project)  # Переход к следующему состоянию
        else:
            # Клавиатура для розничных клиентов
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Памятники", callback_data="Памятники")],
                    [InlineKeyboardButton(text="Другие изделия", callback_data="Другие изделия")]
                ]
            )

            await callback_query.message.answer(
                "Пожалуйста, выберите категорию: Памятники или Другие изделия.",
                reply_markup=keyboard
            )
            await state.set_state(Form.item_interest)  # Переход к следующему состоянию
    except Exception as e:
        logger.error(f"Ошибка в обработке выбора типа клиента: {e}", exc_info=True)
        await callback_query.message.answer("Произошла ошибка при выборе типа клиента. Попробуйте снова.")
