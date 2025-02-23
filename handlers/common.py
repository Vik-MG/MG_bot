# handlers/common.py
from aiogram import types
from aiogram.fsm.context import FSMContext
from core.utils.file_utils import save_file
from core.utils.logging_utils import setup_logger
from aiogram import Bot
from core.states import Form
from core.utils.locales import get_text, load_user_languages  # Добавлен импорт локализации

# Настройка логгера
logger = setup_logger(__name__)

def update_comment(existing_comment: str, new_text: str) -> str:
    """
    Обновляет комментарий, объединяя старый текст с новым.

    Args:
        existing_comment (str): Текущий комментарий.
        new_text (str): Новый текст для добавления.

    Returns:
        str: Обновлённый комментарий.
    """
    return f"{existing_comment}\n{new_text}".strip() if existing_comment else new_text

async def process_input(message: types.Message, state: FSMContext, bot: Bot):
    """
    Универсальная функция для обработки текстовых сообщений и файлов.

    Args:
        message (types.Message): Сообщение от пользователя.
        state (FSMContext): Текущее состояние FSM.
        bot (Bot): Экземпляр Telegram Bot.
    """
    try:
        user_id = message.from_user.id
        data = await state.get_data()

        # Получаем язык пользователя (из FSM или из сохраненных данных)
        lang = data.get("language", load_user_languages().get(str(user_id), "ru"))
        
        # Извлекаем текущие данные FSM
        combined_comment = data.get("combined_comment", "")
        file_list = data.get("file_list", [])
        comment_count = data.get("comment_count", 0)

        if not isinstance(file_list, list):
            file_list = [file_list]

        # Обработка файлов (фото, документы)
        if message.content_type in ["photo", "document"]:
            file_path = await save_file(message, bot)
            file_list.append(file_path)
            await state.update_data(file_list=file_list)

            if message.caption:
                combined_comment = update_comment(combined_comment, message.caption)
                await state.update_data(combined_comment=combined_comment)
                await message.answer(get_text(lang, "send_contact"))
                await state.set_state(Form.contacts)
                return

            await message.answer(get_text(lang, "comment_to_files"))
            return

        # Обработка текстовых сообщений
        if message.content_type == "text" and message.text.strip():
            combined_comment = update_comment(combined_comment, message.text.strip())
            comment_count += 1
            await state.update_data(combined_comment=combined_comment, comment_count=comment_count)

            if comment_count >= 2:
                await message.answer(get_text(lang, "thank_you_commant_2"))
                await state.set_state(Form.contacts)
                return

            await message.answer(get_text(lang, "send_more_details"))
            return

        # Неподдерживаемый тип данных
        await message.answer(get_text(lang, "unsupported_type"))

    except Exception as e:
        logger.error(f"Ошибка при обработке данных пользователя {user_id}: {e}", exc_info=True)
        await message.answer(get_text(lang, "error_occurred"))
