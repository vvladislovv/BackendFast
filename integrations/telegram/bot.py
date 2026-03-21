"""Telegram бот для управления контентом."""
import asyncio
import os
import signal
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession

from core.config import settings
from integrations.telegram.handlers import register_handlers
from utils.logger import get_logger

logger = get_logger()

# API URL для запросов
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Создаем сессию с увеличенным timeout
session = AiohttpSession(timeout=60)
bot = Bot(token=settings.telegram_bot_token, session=session)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


async def set_bot_commands():
    """Установить команды бота."""
    commands = [
        BotCommand(command="start", description="Начать работу"),
    ]
    await bot.set_my_commands(commands)


async def health_check():
    """Проверка здоровья бота."""
    try:
        me = await bot.get_me()
        logger.info(f"✅ Bot is healthy: @{me.username}")
        return True
    except Exception as e:
        logger.error(f"❌ Bot health check failed: {e}")
        return False


async def start_bot():
    """Запустить бота."""
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Запуск Telegram бота (попытка {attempt}/{max_retries})...")
            logger.info(f"API URL: {API_URL}")
            logger.info(f"Admin IDs: {settings.telegram_admin_ids}")
            
            # Проверка здоровья бота
            if not await health_check():
                raise Exception("Health check failed")
            
            register_handlers(dp, API_URL)
            await set_bot_commands()
            
            logger.info("✅ Telegram бот запущен и готов к работе")
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
            break
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска бота (попытка {attempt}/{max_retries}): {e}")
            
            if attempt < max_retries:
                logger.info(f"⏳ Повторная попытка через {retry_delay} секунд...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Экспоненциальная задержка
            else:
                logger.error("❌ Все попытки запуска исчерпаны")
                raise
        finally:
            # Закрываем сессию при выходе
            if attempt == max_retries or 'break' in locals():
                await bot.session.close()


async def shutdown(sig):
    """Graceful shutdown."""
    logger.info(f"Получен сигнал {sig}, завершение работы...")
    await bot.session.close()
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    # Настройка обработчиков сигналов
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig, 
            lambda s=sig: asyncio.create_task(shutdown(s))
        )
    
    try:
        loop.run_until_complete(start_bot())
    except KeyboardInterrupt:
        logger.info("Получен KeyboardInterrupt, завершение...")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
    finally:
        loop.close()
        logger.info("Бот остановлен")
