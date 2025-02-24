# handlers/start.py
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from core.states import Form
from core.utils.logging_utils import setup_logger
from core.utils.locales import get_text, save_user_language  # Добавлен импорт локализации

# Настройка логгера
logger = setup_logger(__name__)

# Создаем роутер
router = Router()

@router.message(Command(commands=["start"]))
async def start_command(message: Message, state: FSMContext):
    """
    Обработка команды /start с учетом языка Telegram.
    """
    try:
        user_id = message.from_user.id
        user_lang = getattr(message.from_user, "language_code", "ru")[:2]  # Определение языка пользователя

        # Проверка поддерживаемых языков, если не поддерживается – устанавливается русский
        supported_languages = ["ru", "uk", "pl", "en"]
        user_lang = user_lang if user_lang in supported_languages else "en"
        await message.answer("⚠ Your language is not supported. Defaulting to English. You can change it in the menu.")


        await state.update_data(language=user_lang)  # Сохраняем язык в FSM
        save_user_language(user_id, user_lang)  # Сохраняем язык в JSON

        logger.info(f"Пользователь {user_id} вызвал команду /start. Определен язык: {user_lang}")

        # Отправляем сообщение с учетом языка
        await message.answer(get_text(user_lang, "greeting"))

        # Устанавливаем следующее состояние
        await state.set_state(Form.client_type)

    except Exception as e:
        logger.error(f"Ошибка в /start у пользователя {user_id}: {e}", exc_info=True)
        await message.answer(get_text(user_lang, "error_occurred"))
