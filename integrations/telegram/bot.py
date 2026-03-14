"""Telegram бот для управления контентом."""
import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage

from core.config import settings
from integrations.telegram.handlers import register_handlers
from utils.logger import get_logger

logger = get_logger()

# API URL для запросов
API_URL = os.getenv("API_URL", "http://localhost:8000")

bot = Bot(token=settings.telegram_bot_token)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


async def set_bot_commands():
    """Установить команды бота."""
    commands = [
        BotCommand(command="start", description="Начать работу"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="vacancies", description="Список вакансий"),
        BotCommand(command="reviews", description="Список отзывов"),
        BotCommand(command="articles", description="Список статей"),
        BotCommand(command="cases", description="Список кейсов"),
    ]
    await bot.set_my_commands(commands)


async def start_bot():
    """Запустить бота."""
    logger.info("Запуск Telegram бота...")
    logger.info(f"API URL: {API_URL}")
    logger.info(f"Admin IDs: {settings.telegram_admin_ids}")
    
    register_handlers(dp, API_URL)
    await set_bot_commands()
    
    logger.info("Telegram бот запущен и готов к работе")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}", exc_info=True)
