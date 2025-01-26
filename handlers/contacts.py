# handlers/contacts.py
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from core.google_sheets import initialize_google_sheet, get_google_sheet
from core.utils.logging_utils import setup_logger
from core.states import Form

# Настройка логгера
logger = setup_logger(__name__)

# Создаём Router
router = Router()

@router.message(Form.contacts)
async def get_contacts(message: types.Message, state: FSMContext):
    """Обработка ввода контактов и сохранение данных в Google Sheets."""
    try:
        logger.info(f"Начало обработки контактов. Пользователь: {message.from_user.id}, Контакты: {message.text}")
        contacts = message.text
        await state.update_data(contacts=contacts)

        # Получаем данные FSM
        data = await state.get_data()
        logger.debug(f"Получены данные FSM: {data}")

        # Объединение файлов и комментариев
        combined_comment = data.get("combined_comment", "").strip()
        file_list = data.get("file_list", [])
        if isinstance(file_list, str):
            file_list = [file_list]
        combined_files = ", ".join(file_list)

        def prepare_data_and_headers(client_type: str):
            """Формирует заголовки и строки для Google Sheets."""
            if client_type == "оптовый":
                sheet_name = "Оптовые клиенты"
                headers = ["Имя клиента", "ID клиента", "Проект", "Файлы", "Комментарий", "Контакты"]
                row = [
                    data.get("name", ""),
                    message.from_user.id,
                    data.get("opt_project", ""),
                    combined_files,
                    combined_comment,
                    contacts
                ]
            elif client_type == "розничный":
                sheet_name = "Розничные клиенты"
                headers = ["Имя клиента", "ID клиента", "Проект", "Кладбище", "Файлы", "Комментарий", "Контакты"]
                row = [
                    data.get("name", ""),
                    message.from_user.id,
                    data.get("item_interest", ""),
                    data.get("cemetery", ""),
                    combined_files,
                    combined_comment,
                    contacts
                ]
            else:
                logger.error("Неизвестный тип клиента.")
                return None, None, None
            return sheet_name, headers, row

        # Определяем тип клиента
        client_type = data.get("client_type", "").lower()
        sheet_name, headers, row = prepare_data_and_headers(client_type)

        if not sheet_name:
            await message.answer("Ошибка: тип клиента не указан. Обратитесь к администратору.")
            return

        # Инициализация и запись в Google Sheets
        try:
            worksheet = await get_google_sheet(sheet_name)
            logger.debug(f"Лист {sheet_name} успешно получен.")

            await initialize_google_sheet(worksheet, headers)
            logger.debug(f"Заголовки {headers} успешно инициализированы.")

            await worksheet.append_row(row)
            logger.info(f"Данные сохранены: {row} в лист: {sheet_name}")

            await message.answer("Спасибо! Ваш запрос сохранён. Мы свяжемся с вами в ближайшее время.")
        except Exception as e:
            logger.error(f"Ошибка записи в Google Sheets: {e}", exc_info=True)
            await message.answer("Произошла ошибка при записи данных в Google Sheets. Попробуйте позже.")
    except Exception as e:
        logger.error(f"Общая ошибка в обработке контактов: {e}", exc_info=True)
        await message.answer("Произошла ошибка. Попробуйте ещё раз позже.")
    finally:
        logger.info(f"FSM завершается для пользователя {message.from_user.id}.")
        await state.clear()
