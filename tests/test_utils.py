# tests/test_utils.py
import pytest
from unittest.mock import AsyncMock, patch
from core.utils.file_utils import save_file
from aiogram.types import Message, Document, PhotoSize


@pytest.mark.asyncio
@patch("core.utils.file_utils.os.makedirs")
@patch("core.utils.file_utils.Bot.get_file")
@patch("core.utils.file_utils.Bot.download_file")
async def test_save_file_document(mock_download_file, mock_get_file, mock_makedirs):
    """
    Тестирование сохранения документов через save_file.
    """
    message = AsyncMock(spec=Message)
    message.document = Document(file_id="doc_id", file_name="test_document.txt")
    message.content_type = "document"

    bot = AsyncMock()
    mock_get_file.return_value.file_path = "path/to/document.txt"
    mock_download_file.return_value = None

    result = await save_file(message, bot)

    assert result == "uploads/test_document.txt"
    mock_makedirs.assert_called_once_with("uploads", exist_ok=True)
    mock_get_file.assert_called_once_with("doc_id")
    mock_download_file.assert_called_once_with("path/to/document.txt", "uploads/test_document.txt")


@pytest.mark.asyncio
@patch("core.utils.file_utils.os.makedirs")
@patch("core.utils.file_utils.Bot.get_file")
@patch("core.utils.file_utils.Bot.download_file")
async def test_save_file_photo(mock_download_file, mock_get_file, mock_makedirs):
    """
    Тестирование сохранения фотографий через save_file.
    """
    message = AsyncMock(spec=Message)
    message.photo = [PhotoSize(file_id="photo_id", width=800, height=600)]
    message.content_type = "photo"

    bot = AsyncMock()
    mock_get_file.return_value.file_path = "path/to/photo.jpg"
    mock_download_file.return_value = None

    result = await save_file(message, bot)

    assert result == "uploads/photo.jpg"
    mock_makedirs.assert_called_once_with("uploads", exist_ok=True)
    mock_get_file.assert_called_once_with("photo_id")
    mock_download_file.assert_called_once_with("path/to/photo.jpg", "uploads/photo.jpg")


@pytest.mark.asyncio
async def test_save_file_unsupported():
    """
    Тестирование ошибки при попытке сохранить неподдерживаемый тип сообщения.
    """
    message = AsyncMock(spec=Message)
    message.content_type = "text"  # Неподдерживаемый тип

    bot = AsyncMock()

    with pytest.raises(ValueError, match="Unsupported content type: text"):
        await save_file(message, bot)
