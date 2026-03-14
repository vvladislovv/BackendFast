"""Проверка прав администратора."""
from aiogram.types import Message, CallbackQuery
from typing import Union

from core.config import settings
from utils.logger import get_logger

logger = get_logger()


def is_admin(user_id: int) -> bool:
    """Проверить, является ли пользователь администратором."""
    is_admin_user = user_id in settings.admin_ids_list
    logger.info(f"Проверка админа для user_id={user_id}: {is_admin_user}")
    return is_admin_user


async def admin_only(event: Union[Message, CallbackQuery]) -> bool:
    """Фильтр для проверки прав администратора."""
    # Получаем user_id в зависимости от типа события
    if isinstance(event, CallbackQuery):
        user_id = event.from_user.id
    else:
        user_id = event.from_user.id
    
    if not is_admin(user_id):
        logger.warning(f"Неавторизованный доступ от user_id={user_id}")
        return False
    return True
