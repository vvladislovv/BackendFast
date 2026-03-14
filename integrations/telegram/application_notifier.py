"""Уведомления о новых заявках в Telegram."""
import asyncio
from pathlib import Path
from aiogram import Bot
from aiogram.types import FSInputFile
from core.config import settings
from utils.logger import get_logger

logger = get_logger()


async def notify_new_application(application_data: dict):
    """Отправить уведомление админу о новой заявке."""
    try:
        bot = Bot(token=settings.telegram_bot_token)
        
        text = (
            "🆕 <b>Новая заявка с сайта!</b>\n\n"
            f"<b>ID:</b> {application_data['id']}\n"
            f"<b>Имя:</b> {application_data['name']}\n"
        )
        
        if application_data.get('company'):
            text += f"<b>Компания:</b> {application_data['company']}\n"
        
        text += f"<b>Email:</b> {application_data['email']}\n"
        
        if application_data.get('phone'):
            text += f"<b>Телефон:</b> {application_data['phone']}\n"
        
        text += f"\n<b>Сообщение:</b>\n{application_data['message']}"
        
        # Отправляем всем админам
        for admin_id in settings.admin_ids_list:
            try:
                # Если есть файл, отправляем его вместе с текстом в одном сообщении
                if application_data.get('file_path'):
                    file_path = Path(application_data['file_path'])
                    if file_path.exists():
                        try:
                            file = FSInputFile(file_path)
                            await bot.send_document(
                                chat_id=admin_id,
                                document=file,
                                caption=text,
                                parse_mode="HTML"
                            )
                            logger.info(f"Заявка с файлом отправлена админу {admin_id}")
                        except Exception as e:
                            logger.error(f"Ошибка отправки файла админу {admin_id}: {e}")
                            # Если не удалось отправить с файлом, отправляем только текст
                            await bot.send_message(
                                chat_id=admin_id,
                                text=text,
                                parse_mode="HTML"
                            )
                    else:
                        logger.warning(f"Файл не найден: {file_path}")
                        # Отправляем только текст
                        await bot.send_message(
                            chat_id=admin_id,
                            text=text,
                            parse_mode="HTML"
                        )
                else:
                    # Если файла нет, отправляем только текст
                    await bot.send_message(
                        chat_id=admin_id,
                        text=text,
                        parse_mode="HTML"
                    )
                
                logger.info(f"Уведомление о заявке {application_data['id']} отправлено админу {admin_id}")
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления админу {admin_id}: {e}")
        
        await bot.session.close()
        
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления о заявке: {e}", exc_info=True)
