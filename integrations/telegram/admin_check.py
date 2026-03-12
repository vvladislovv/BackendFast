"""Проверка прав администратора."""
from aiogram.types import Message

from core.config import settings
from utils.logger import get_logger

logger = get_logger()


def is_admin(user_id: int) -> bool:
    """Проверить, является ли пользователь администратором."""
    is_admin_user = user_id in settings.admin_ids_list
    logger.info(f"Проверка админа для user_id={user_id}: {is_admin_user}")
    return is_admin_user


async def admin_only(message: Message) -> bool:
    """Фильтр для проверки прав администратора."""
    if not is_admin(message.from_user.id):
        logger.warning(f"Неавторизованный доступ от user_id={message.from_user.id}")
        return False
    return True
