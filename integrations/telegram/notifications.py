"""Отправка уведомлений в Telegram."""
from aiogram import Bot
from core.config import settings
from models.application import Application
from utils.logger import get_logger

logger = get_logger()


async def send_new_application_notification(application: Application):
    """Отправить уведомление о новой заявке админу."""
    try:
        bot = Bot(token=settings.telegram_bot_token)
        
        text = (
            f"🆕 <b>Новая заявка с сайта!</b>\n\n"
            f"<b>ID:</b> {application.id}\n"
            f"<b>Имя:</b> {application.name}\n"
            f"<b>Email:</b> {application.email}\n"
        )
        
        if application.phone:
            text += f"<b>Телефон:</b> {application.phone}\n"
        
        text += f"\n<b>Сообщение:</b>\n{application.message}"
        
        # Отправить всем админам
        for admin_id in settings.telegram_admin_ids:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=text,
                    parse_mode="HTML"
                )
                logger.info(f"Уведомление о заявке {application.id} отправлено админу {admin_id}")
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления админу {admin_id}: {e}")
        
        await bot.session.close()
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления о заявке: {e}")
