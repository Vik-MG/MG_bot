# tests/test_google_sheets.py
import pytest
from unittest.mock import AsyncMock, patch
from core.google_sheets import get_google_sheet, initialize_google_sheet

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
    """
    Тестирование инициализации заголовков на листе.
    """
    mock_worksheet = AsyncMock()
    mock_row_values.return_value = ["Existing Header"]
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
