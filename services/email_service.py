"""Сервис для отправки email уведомлений."""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

from core.config import settings
from utils.logger import get_logger

logger = get_logger()


async def send_email(to_email: str, subject: str, html_content: str, text_content: str = None):
    """
    Отправить email.
    
    Args:
        to_email: Email получателя
        subject: Тема письма
        html_content: HTML контент письма
        text_content: Текстовый контент (опционально)
    """
    try:
        # Создаем сообщение
        message = MIMEMultipart("alternative")
        message["From"] = settings.email_from
        message["To"] = to_email
        message["Subject"] = subject
        
        # Добавляем текстовую версию если есть
        if text_content:
            part1 = MIMEText(text_content, "plain", "utf-8")
            message.attach(part1)
        
        # Добавляем HTML версию
        part2 = MIMEText(html_content, "html", "utf-8")
        message.attach(part2)
        
        # Отправляем email
        await aiosmtplib.send(
            message,
            hostname=settings.email_host,
            port=settings.email_port,
            username=settings.email_user,
            password=settings.email_password,
            use_tls=True,
            timeout=10,
        )
        
        logger.info(f"✅ Email отправлен на {to_email}: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка отправки email на {to_email}: {e}", exc_info=True)
        return False


async def send_admin_notification(application_data: dict):
    """
    Отправить уведомление админу о новой заявке.
    
    Args:
        application_data: Данные заявки
    """
    subject = f"🆕 Новая заявка #{application_data['id']} от {application_data['name']}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ background: #f9f9f9; padding: 20px; border: 1px solid #ddd; border-radius: 0 0 5px 5px; }}
            .field {{ margin: 10px 0; padding: 10px; background: white; border-left: 3px solid #4CAF50; }}
            .label {{ font-weight: bold; color: #4CAF50; }}
            .footer {{ margin-top: 20px; text-align: center; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🆕 Новая заявка с сайта</h2>
            </div>
            <div class="content">
                <div class="field">
                    <span class="label">ID заявки:</span> {application_data['id']}
                </div>
                <div class="field">
                    <span class="label">Имя:</span> {application_data['name']}
                </div>
                {f'<div class="field"><span class="label">Компания:</span> {application_data["company"]}</div>' if application_data.get('company') else ''}
                <div class="field">
                    <span class="label">Email:</span> <a href="mailto:{application_data['email']}">{application_data['email']}</a>
                </div>
                {f'<div class="field"><span class="label">Телефон:</span> {application_data["phone"]}</div>' if application_data.get('phone') else ''}
                <div class="field">
                    <span class="label">Сообщение:</span><br>
                    {application_data['message'].replace(chr(10), '<br>')}
                </div>
                {f'<div class="field"><span class="label">Файл:</span> Прикреплен</div>' if application_data.get('file_path') else ''}
            </div>
            <div class="footer">
                <p>Это автоматическое уведомление от системы HackTaika</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Новая заявка с сайта
    
    ID: {application_data['id']}
    Имя: {application_data['name']}
    {'Компания: ' + application_data['company'] if application_data.get('company') else ''}
    Email: {application_data['email']}
    {'Телефон: ' + application_data['phone'] if application_data.get('phone') else ''}
    
    Сообщение:
    {application_data['message']}
    
    {'Файл: Прикреплен' if application_data.get('file_path') else ''}
    """
    
    return await send_email(settings.email_admin, subject, html_content, text_content)


async def send_welcome_email(client_email: str, client_name: str):
    """
    Отправить приветственное письмо клиенту.
    
    Args:
        client_email: Email клиента
        client_name: Имя клиента
    """
    subject = "Спасибо за вашу заявку! | HackTaika"
    
    # Читаем шаблон из файла
    template_path = Path("templates/welcome_email.html")
    
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            html_content = f.read()
            # Заменяем плейсхолдеры
            html_content = html_content.replace("{{client_name}}", client_name)
    else:
        # Если шаблон не найден, используем простой HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #4CAF50; color: white; padding: 30px; text-align: center; border-radius: 5px 5px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
                .footer {{ background: #333; color: white; padding: 20px; text-align: center; border-radius: 0 0 5px 5px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Спасибо за вашу заявку!</h1>
                </div>
                <div class="content">
                    <p>Здравствуйте, {client_name}!</p>
                    
                    <p>Мы получили вашу заявку и благодарим вас за интерес к нашим услугам.</p>
                    
                    <p>Наш менеджер свяжется с вами в ближайшее время для обсуждения деталей.</p>
                    
                    <p>Если у вас есть срочные вопросы, вы можете связаться с нами:</p>
                    <ul>
                        <li>Email: <a href="mailto:info@hacktaika.ru">info@hacktaika.ru</a></li>
                        <li>Телефон: +7 (XXX) XXX-XX-XX</li>
                    </ul>
                    
                    <p style="text-align: center;">
                        <a href="https://hacktaika.ru" class="button">Посетить наш сайт</a>
                    </p>
                </div>
                <div class="footer">
                    <p>С уважением,<br>Команда HackTaika</p>
                    <p style="font-size: 12px; margin-top: 10px;">
                        © 2026 HackTaika. Все права защищены.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    text_content = f"""
    Здравствуйте, {client_name}!
    
    Мы получили вашу заявку и благодарим вас за интерес к нашим услугам.
    
    Наш менеджер свяжется с вами в ближайшее время для обсуждения деталей.
    
    Если у вас есть срочные вопросы, вы можете связаться с нами:
    - Email: info@hacktaika.ru
    - Телефон: +7 (XXX) XXX-XX-XX
    
    С уважением,
    Команда HackTaika
    """
    
    return await send_email(client_email, subject, html_content, text_content)
