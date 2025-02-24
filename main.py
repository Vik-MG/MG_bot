# main.py
import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiohttp import web
from core.config import BOT_TOKEN, WEBHOOK_URL
from handlers import register_all_handlers
from core.utils.locales import get_text, load_user_languages  # Импорт мультиязычности

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
        BotCommand(command="/start", description=get_text("ru", "start_command")),  # Используем мультиязычность
    ]
    await bot.set_my_commands(commands)

async def on_startup(app: web.Application):
    """Функция запуска при старте сервера."""
    register_all_handlers(dp)
    await set_commands(bot)
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(get_text("ru", "bot_started_with_webhook"))  # Используем мультиязычность

async def webhook_handler(request: web.Request):
    """Обработчик запросов от Telegram."""
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return web.Response()

app = web.Application()
app.router.add_post("/webhook", webhook_handler)
app.on_startup.append(on_startup)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=8080)
