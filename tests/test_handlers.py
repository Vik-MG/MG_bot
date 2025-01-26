# tests/test_handlers.py
import pytest
from unittest.mock import AsyncMock, patch
from aiogram.types import Message, PhotoSize, Document
from aiogram.fsm.context import FSMContext
from core.utils.file_utils import save_file
from handlers.common import process_input

@pytest.mark.asyncio
async def test_process_input_text():
    """
    Test process_input function for handling text messages.
    """
    message = AsyncMock(spec=Message)
    message.content_type = "text"
    message.text = "Test comment"
    message.from_user.id = 12345

    state = AsyncMock(spec=FSMContext)
    state.get_data.return_value = {}

    await process_input(message, state, bot=None)

    state.update_data.assert_called_once_with({"combined_comment": "Test comment"})
    message.answer.assert_called_once_with(
        "Вы можете также прислать фото или проект, если есть. Напишите дополнительный комментарий или любое сообщение."
    )

@pytest.mark.asyncio
async def test_process_input_photo():
    """
    Test process_input function for handling photo messages.
    """
    message = AsyncMock(spec=Message)
    message.content_type = "photo"
    message.photo = [PhotoSize(file_id="photo_id", width=800, height=600)]
    message.caption = "Photo caption"
    message.from_user.id = 12345

    state = AsyncMock(spec=FSMContext)
    state.get_data.return_value = {}

    with patch("core.utils.file_utils.save_file", new=AsyncMock(return_value="path/to/photo.jpg")) as mock_save_file:
        await process_input(message, state, bot=None)

        mock_save_file.assert_called_once_with(message, None)
        state.update_data.assert_any_call({"file_list": ["path/to/photo.jpg"]})
        state.update_data.assert_any_call({"combined_comment": "Photo caption"})
        message.answer.assert_called_once_with(
            "Файлы и комментарий сохранены. Напишите ваш номер телефона для связи с менеджером."
        )

@pytest.mark.asyncio
async def test_process_input_document():
    """
    Test process_input function for handling document messages.
    """
    message = AsyncMock(spec=Message)
    message.content_type = "document"
    message.document = Document(file_id="doc_id", file_name="example.txt")
    message.from_user.id = 12345

    state = AsyncMock(spec=FSMContext)
    state.get_data.return_value = {"file_list": []}

    with patch("core.utils.file_utils.save_file", new=AsyncMock(return_value="path/to/example.txt")) as mock_save_file:
        await process_input(message, state, bot=None)

        mock_save_file.assert_called_once_with(message, None)
        state.update_data.assert_called_once_with({"file_list": ["path/to/example.txt"]})
        message.answer.assert_called_once_with("Напишите, пожалуйста, комментарий к вашим файлам.")

@pytest.mark.asyncio
async def test_process_input_error():
    """
    Test process_input function for handling unexpected errors.
    """
    message = AsyncMock(spec=Message)
    message.content_type = "photo"
    message.photo = [PhotoSize(file_id="photo_id", width=800, height=600)]
    message.caption = "Photo caption"
    message.from_user.id = 12345

    state = AsyncMock(spec=FSMContext)
    state.get_data.return_value = {}

    with patch("core.utils.file_utils.save_file", side_effect=Exception("Unexpected Error")):
        await process_input(message, state, bot=None)

        message.answer.assert_called_once_with(
            "Произошла ошибка при обработке вашего запроса. Попробуйте снова или обратитесь за поддержкой."
        )
