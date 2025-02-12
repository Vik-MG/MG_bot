# handlers/start.py
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext  # Новый подход для FSM
from core.states import Form
from core.utils.logging_utils import setup_logger

# Настройка логгера
logger = setup_logger(__name__)

# Создаем роутер
router = Router()

@router.message(Command(commands=["start"]))
async def start_command(message: Message, state: FSMContext):
    """
    Обработка команды /start.
    """
    try:
        logger.info(f"Пользователь {message.from_user.id} вызвал команду /start.")
        await message.answer("Здравствуйте! Как я могу к вам обращаться?")
        
        # Установка нового состояния через FSMContext
        await state.set_state(Form.client_type)
    except Exception as e:
        logger.error(f"Ошибка при обработке команды /start для пользователя {message.from_user.id}: {e}", exc_info=True)
        await message.answer("Произошла ошибка. Попробуйте снова позже.")


