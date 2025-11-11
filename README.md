# Telegram Bot Project

## Описание
Данный проект представляет собой Telegram-бота, разработанного на основе библиотеки `Aiogram 3.x`. Бот поддерживает:
- Асинхронное взаимодействие с Google Sheets.
- Управление состояниями через Finite State Machine (FSM).
- Логирование действий и ошибок.

## Структура проекта
project/ 
├── core/ 
│ ├── config.py # Конфигурации 
│ ├── google_sheets.py # Асинхронная работа с Google Sheets 
│ ├── google_drive.py # # Хранение загруженных файлов в облаке
│ ├── states.py # FSM состояния 
│ ├── utils/ 
│ ├── file_utils.py # Работа с файлами 
│ ├── logging_utils.py # Логирование 
│ ├── google_utils.py # Утилиты для Google API 
├── handlers/ 
│ ├── init.py # Регистрация обработчиков через Router 
│ ├── start.py # Команда /start 
│ ├── client_type.py # Логика выбора клиента 
│ ├── common.py # Общие функции 
│ ├── contacts.py # Обработка контактов 
│ ├── retail.py # Логика для розничных клиентов 
│ ├── wholesale.py # Логика для оптовых клиентов 
│ ├── manager.py # Взаимодействие с мене 
├── tests/ 
│ ├── test_handlers.py # Тесты для обработчиков 
│ ├── test_utils.py # Тесты для утилит 
│ ├── test_google_sheets.py # Тесты для Google Sheets 
│ ├── test_google_drive.py # Тесты для Google Drive
├── uploads/ # Хранение загруженных файлов 
├── .env # Переменные окружения 
├── client_secret_*.json # Учетные данные Google API 
├── main.py # Основная точка входа 
├── requirements.txt # Зависимости проекта 
├── README.md # Документация

bash
Копировать
Редактировать

## Установка

### 1. Клонируйте репозиторий:
```bash
git clone <URL>
cd <project-folder>
2. Установите зависимости:
bash
Копировать
Редактировать
pip install -r requirements.txt
3. Настройте переменные окружения:
Создайте файл .env в корне проекта и добавьте следующие параметры:

makefile
Копировать
Редактировать
BOT_TOKEN=<ваш_токен_бота>
CREDENTIALS_FILE=<путь_к_файлу_учётных_данных_Google_API>
SPREADSHEET_ID=<ID_вашей_таблицы_Google_Sheets>
4. Запустите бота:
bash
Копировать
Редактировать
python main.py
Регистрация обработчиков через Router
В новой структуре все обработчики регистрируются через Router. Пример из handlers/__init__.py:

python
Копировать
Редактировать
from aiogram import Router
from .start import router as start_router
from .client_type import router as client_type_router

def register_all_handlers(router: Router):
    router.include_router(start_router)
    router.include_router(client_type_router)
Чтобы добавить новый обработчик:

Создайте файл в папке handlers/ (например, new_handler.py).
Импортируйте и добавьте его в функцию register_all_handlers.
Асинхронная работа с Google Sheets
Бот использует библиотеку gspread-asyncio для взаимодействия с Google Sheets. Основные функции:

get_google_sheet(sheet_name) — подключение к указанному листу.
initialize_google_sheet(sheet, headers) — инициализация заголовков на листе.
Пример использования:

python
Копировать
Редактировать
from core.google_sheets import get_google_sheet, initialize_google_sheet

async def example():
    sheet = await get_google_sheet("TestSheet")
    await initialize_google_sheet(sheet, ["Header1", "Header2"])
Тестирование
Запуск тестов:
bash
Копировать
Редактировать
pytest tests/
Описание тестов:
test_handlers.py: Проверка обработчиков и их взаимодействия с FSM.
test_google_sheets.py: Тестирование взаимодействий с Google Sheets.
test_utils.py: Тестирование утилит для работы с файлами.
Логирование
Логирование настраивается через модуль logging_utils.py. Логи включают:

Уровень (INFO, ERROR и т.д.).
Время выполнения.
Имя модуля и строку вызова.
Пример настройки:

python
Копировать
Редактировать
from core.utils.logging_utils import setup_logger

logger = setup_logger("example_logger", "logs/example.log")
logger.info("Пример логирования.")
Поддержка
Если возникли вопросы, обратитесь к разработчику или создайте issue в репозитории.












