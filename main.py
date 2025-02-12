# main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiohttp import web
from core.config import BOT_TOKEN, WEBHOOK_URL
from handlers import register_all_handlers

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

async def on_startup(app: web.Application):
    """Функция запуска при старте сервера."""
    register_all_handlers(dp)
    await set_commands(bot)
    await bot.set_webhook(WEBHOOK_URL)
    logging.info("Бот запущен с Webhook!")

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

