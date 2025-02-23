# main.py
import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiohttp import web
from core.config import BOT_TOKEN, WEBHOOK_URL, USE_WEBHOOK  # Добавлен USE_WEBHOOK
from handlers import register_all_handlers

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Проверка токена
if not BOT_TOKEN:
    logger.error("❌ Токен бота не задан! Приложение завершено.")
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

async def on_startup():
    """Функция запуска при старте бота."""
    try:
        register_all_handlers(dp)
        await set_commands(bot)

        if USE_WEBHOOK:  # Добавлена логика переключения Webhook/Polling
            if not WEBHOOK_URL:
                logger.error("❌ Переменная WEBHOOK_URL не задана!")
                exit("Ошибка: WEBHOOK_URL обязателен для работы Webhook.")
            await bot.set_webhook(WEBHOOK_URL)
            logger.info(f"✅ Бот запущен с Webhook: {WEBHOOK_URL}")
        else:
            await bot.delete_webhook()
            logger.info("✅ Бот запущен в режиме Polling")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        exit(1)

async def webhook_handler(request: web.Request):
    """Обработчик запросов от Telegram."""
    try:
        update = await request.json()
        await dp.feed_webhook_update(bot, update)
        return web.Response()
    except Exception as e:
        logger.error(f"Ошибка при обработке webhook: {e}")
        return web.Response(status=500)

async def on_shutdown():
    """Функция корректного завершения работы бота."""
    logger.info("🛑 Завершение работы бота...")
    await dp.storage.close()
    await dp.storage.wait_closed()

async def main():
    """Главная функция запуска."""
    await on_startup()
    
    if USE_WEBHOOK:
        app = web.Application()
        app.router.add_post("/webhook", webhook_handler)
        app.on_shutdown.append(on_shutdown)
        logger.info("🌍 Запуск Webhook-сервера...")
        web.run_app(app, host=os.getenv("HOST", "0.0.0.0"), port=int(os.getenv("PORT", 8080)))
    else:
        logger.info("🤖 Запуск Polling...")
        try:
            await dp.start_polling(bot)
        except Exception as e:
            logger.error(f"Ошибка в режиме Polling: {e}")
        finally:
            await on_shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹ Бот остановлен вручную.")
