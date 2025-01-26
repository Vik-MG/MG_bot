# main.py
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from core.config import BOT_TOKEN
from handlers import register_all_handlers
from aiogram.types import BotCommand
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Проверка токена
if not BOT_TOKEN:
    logging.error("Токен бота не задан! Приложение завершено.")
    exit("Ошибка: BOT_TOKEN обязателен для запуска бота.")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


async def set_commands(bot: Bot):
    """Установка команд бота."""
    commands = [
        BotCommand(command="/start", description="Запустить бота"),
    ]
    await bot.set_my_commands(commands)


async def main():
    """Главная точка входа в приложение."""
    try:
        # Регистрация обработчиков
        register_all_handlers(dp)
        logging.info("Обработчики успешно зарегистрированы.")

        # Установка команд
        await set_commands(bot)

        # Запуск polling
        logging.info("Бот запущен. Ожидание сообщений...")
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Критическая ошибка при запуске: {e}", exc_info=True)
    finally:
        # Закрытие соединения бота
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())