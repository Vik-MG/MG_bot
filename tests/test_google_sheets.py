# tests/test_google_sheets.py
import logging
import pytest
from unittest.mock import AsyncMock, patch
from core.google_sheets import get_google_sheet, initialize_google_sheet
from core.utils.logging_utils import setup_logger

# Настройка логгера
logger = setup_logger("core.google_sheets")

@pytest.mark.asyncio
@patch("core.google_sheets.agcm.authorize", new_callable=AsyncMock)
async def test_get_google_sheet_existing(mock_authorize):
    """
    Тестирование получения существующего листа.
    """
    mock_client = AsyncMock()
    mock_spreadsheet = AsyncMock()
    mock_worksheet = AsyncMock()

    mock_authorize.return_value = mock_client
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_spreadsheet.worksheet.return_value = mock_worksheet

    sheet = await get_google_sheet(sheet_name="TestSheet")
    assert sheet == mock_worksheet
    mock_client.open_by_key.assert_called_once()
    mock_spreadsheet.worksheet.assert_called_once_with("TestSheet")


@pytest.mark.asyncio
@patch("core.google_sheets.agcm.authorize", new_callable=AsyncMock)
async def test_get_google_sheet_new(mock_authorize):
    """
    Тестирование создания нового листа, если он не существует.
    """
    mock_client = AsyncMock()
    mock_spreadsheet = AsyncMock()
    mock_worksheet = AsyncMock()

    mock_authorize.return_value = mock_client
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_spreadsheet.worksheet.side_effect = Exception("Sheet not found")
    mock_spreadsheet.add_worksheet.return_value = mock_worksheet

    sheet = await get_google_sheet(sheet_name="NewSheet")
    assert sheet == mock_worksheet
    mock_spreadsheet.add_worksheet.assert_called_once_with(title="NewSheet", rows=100, cols=20)


@pytest.mark.asyncio
@patch("core.google_sheets.AsyncioGspreadWorksheet.append_row", new_callable=AsyncMock)
@patch("core.google_sheets.AsyncioGspreadWorksheet.row_values", new_callable=AsyncMock)
async def test_initialize_google_sheet(mock_row_values, mock_append_row):
    mock_worksheet = AsyncMock()
    mock_worksheet.append_row = mock_append_row  # Привязываем мок
    mock_row_values.return_value = []  # Пустой лист

    headers = ["Header1", "Header2"]

    await initialize_google_sheet(mock_worksheet, headers)

    mock_worksheet.clear.assert_called_once()
    mock_append_row.assert_called_once_with(headers)


@pytest.mark.asyncio
@patch("core.google_sheets.agcm.authorize", new_callable=AsyncMock)
async def test_get_google_sheet_error(mock_authorize):
    """
    Тестирование обработки ошибки при доступе к Google Sheets.
    """
    mock_authorize.side_effect = Exception("Authorization Error")

    with pytest.raises(RuntimeError, match="Не удалось получить доступ к Google Sheet"):
        await get_google_sheet(sheet_name="TestSheet")


@pytest.mark.asyncio
@patch("core.google_sheets.AsyncioGspreadWorksheet.append_row", new_callable=AsyncMock)
@patch("core.google_sheets.AsyncioGspreadWorksheet.row_values", new_callable=AsyncMock)
async def test_initialize_google_sheet_existing_headers(mock_row_values, mock_append_row, caplog):
    # Мок объекта Google Sheet
    mock_worksheet = AsyncMock()
    mock_worksheet.append_row = mock_append_row
    mock_worksheet.title = "Test Sheet"

    # Заголовки совпадают
    mock_row_values.return_value = ["Header1", "Header2"]
    headers = ["Header1", "Header2"]

    # Проверка логов и вызов функции
    with caplog.at_level(logging.INFO):
        await initialize_google_sheet(mock_worksheet, headers)

    # Проверка, что clear и append_row не вызваны
    mock_worksheet.clear.assert_not_called()
    mock_worksheet.append_row.assert_not_called()

    # Проверка корректности логов
    assert "Заголовки листа 'Test Sheet' совпадают, обновление не требуется." in caplog.text