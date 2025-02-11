# tests/test_utils.py
import os
import pytest
from unittest.mock import AsyncMock, patch
from core.utils.file_utils import save_file
from aiogram.types import Message, Document, PhotoSize, User


@pytest.mark.asyncio
@patch("core.utils.file_utils.os.makedirs")
@patch("core.utils.file_utils.Bot.get_file")
@patch("core.utils.file_utils.Bot.download_file")
async def test_save_file_document(mock_download_file, mock_get_file, mock_makedirs):
    message = AsyncMock(spec=Message)
    message.document = Document(file_id="doc_id", file_unique_id="unique_doc_id", file_name="test_document.txt")
    message.content_type = "document"
    message.photo = None  # Добавляем, чтобы избежать AttributeError
    message.from_user = User(id=12345, is_bot=False, first_name="TestUser")

    bot = AsyncMock()
    mock_get_file.return_value.file_path = "path/to/document.txt"

    result = await save_file(message, bot)

    expected_path = os.path.join("uploads", "12345", "test_document.txt")
    assert result == expected_path


@pytest.mark.asyncio
@patch("core.utils.file_utils.os.makedirs")
@patch("core.utils.file_utils.Bot.get_file")
@patch("core.utils.file_utils.Bot.download_file")
async def test_save_file_photo(mock_download_file, mock_get_file, mock_makedirs):
    message = AsyncMock(spec=Message)
    message.photo = [PhotoSize(file_id="photo_id", file_unique_id="unique_photo_id", width=800, height=600)]
    message.content_type = "photo"
    message.from_user = User(id=12345, is_bot=False, first_name="TestUser")

    bot = AsyncMock()
    mock_get_file.return_value.file_path = "path/to/photo.jpg"
    mock_download_file.return_value = None

    result = await save_file(message, bot)

    expected_path = os.path.join("uploads", "12345", "photo_photo_id.jpg")
    assert result == expected_path


@pytest.mark.asyncio
async def test_save_file_unsupported():
    """
    Тестирование ошибки при попытке сохранить неподдерживаемый тип сообщения.
    """
    message = AsyncMock(spec=Message)
    message.content_type = "text"  # Неподдерживаемый тип
    message.from_user = User(id=12345, is_bot=False, first_name="TestUser")

    bot = AsyncMock()

    with pytest.raises(ValueError, match="Unsupported content type: text"):
        await save_file(message, bot)

