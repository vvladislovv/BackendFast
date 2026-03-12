"""Обработчики команд Telegram бота."""
from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

from integrations.telegram.admin_check import admin_only
from utils.logger import get_logger

logger = get_logger()


async def cmd_start(message: Message):
    """Обработчик команды /start."""
    logger.info(f"Команда /start от user_id={message.from_user.id}")
    
    if not await admin_only(message):
        return
    
    await message.answer(
        "Привет! Я бот для управления контентом.\n"
        "Используй команды для добавления контента:\n"
        "/add_vacancy - Добавить вакансию\n"
        "/add_review - Добавить отзыв\n"
        "/add_article - Добавить статью\n"
        "/add_case - Добавить кейс"
    )


async def cmd_help(message: Message):
    """Обработчик команды /help."""
    logger.info(f"Команда /help от user_id={message.from_user.id}")
    
    if not await admin_only(message):
        return
    
    await message.answer(
        "Доступные команды:\n"
        "/start - Начать работу\n"
        "/help - Помощь\n"
        "/add_vacancy - Добавить вакансию\n"
        "/add_review - Добавить отзыв\n"
        "/add_article - Добавить статью\n"
        "/add_case - Добавить кейс"
    )



async def cmd_add_vacancy(message: Message):
    """Обработчик команды /add_vacancy."""
    logger.info(f"Команда /add_vacancy от user_id={message.from_user.id}")
    
    if not await admin_only(message):
        return
    
    await message.answer(
        "Для добавления вакансии отправьте данные в формате:\n"
        "Название\nСсылка\nТип занятости\nОписание (опционально)"
    )


async def cmd_add_review(message: Message):
    """Обработчик команды /add_review."""
    logger.info(f"Команда /add_review от user_id={message.from_user.id}")
    
    if not await admin_only(message):
        return
    
    await message.answer(
        "Для добавления отзыва отправьте данные в формате:\n"
        "Имя\nКомпания\nТекст отзыва\nКоличество звезд (1-5)\nСсылка на фото (опционально)"
    )


async def cmd_add_article(message: Message):
    """Обработчик команды /add_article."""
    logger.info(f"Команда /add_article от user_id={message.from_user.id}")
    
    if not await admin_only(message):
        return
    
    await message.answer(
        "Для добавления статьи отправьте данные в формате:\n"
        "Название\nСсылка\nСсылка на фото (опционально)"
    )


async def cmd_add_case(message: Message):
    """Обработчик команды /add_case."""
    logger.info(f"Команда /add_case от user_id={message.from_user.id}")
    
    if not await admin_only(message):
        return
    
    await message.answer(
        "Для добавления кейса отправьте данные в формате:\n"
        "Название\nОписание\nТеги (через запятую)\nСсылка на изображение\nСсылка на проект"
    )


def register_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков."""
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_add_vacancy, Command("add_vacancy"))
    dp.message.register(cmd_add_review, Command("add_review"))
    dp.message.register(cmd_add_article, Command("add_article"))
    dp.message.register(cmd_add_case, Command("add_case"))
