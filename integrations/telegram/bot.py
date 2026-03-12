"""Telegram бот для управления контентом."""
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from core.config import settings
from integrations.telegram.handlers import register_handlers
from utils.logger import get_logger

logger = get_logger()

bot = Bot(token=settings.telegram_bot_token)
dp = Dispatcher()


async def set_bot_commands():
    """Установить команды бота."""
    commands = [
        BotCommand(command="start", description="Начать работу"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="add_vacancy", description="Добавить вакансию"),
        BotCommand(command="add_review", description="Добавить отзыв"),
        BotCommand(command="add_article", description="Добавить статью"),
        BotCommand(command="add_case", description="Добавить кейс"),
    ]
    await bot.set_my_commands(commands)


async def start_bot():
    """Запустить бота."""
    logger.info("Запуск Telegram бота...")
    
    register_handlers(dp)
    await set_bot_commands()
    
    logger.info("Telegram бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_bot())
