"""Тестирование email уведомлений."""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

from services.email_service import send_admin_notification, send_welcome_email
from core.config import settings


async def test_admin_notification():
    """Тест уведомления админу."""
    print("🧪 Тест 1: Отправка уведомления админу")
    print(f"📧 Email админа: {settings.email_admin}")
    
    test_application = {
        "id": 999,
        "name": "Тестовый Клиент",
        "company": "ООО Тест",
        "email": "test@example.com",
        "phone": "+7 999 123-45-67",
        "message": "Это тестовое сообщение для проверки email уведомлений.\n\nМногострочное сообщение работает корректно.",
        "file_path": None
    }
    
    result = await send_admin_notification(test_application)
    
    if result:
        print("✅ Уведомление админу отправлено успешно!")
    else:
        print("❌ Ошибка отправки уведомления админу")
    
    return result


async def test_welcome_email():
    """Тест приветственного письма клиенту."""
    print("\n🧪 Тест 2: Отправка приветственного письма клиенту")
    print(f"📧 Email отправителя: {settings.email_from}")
    
    # Отправляем на тестовый email
    test_email = "vlad.yelcheninov@gmail.com"
    test_name = "Владислав"
    
    print(f"📧 Email получателя: {test_email}")
    
    result = await send_welcome_email(test_email, test_name)
    
    if result:
        print("✅ Приветственное письмо отправлено успешно!")
        print(f"   📬 Проверьте почту: {test_email}")
    else:
        print("❌ Ошибка отправки приветственного письма")
    
    return result


async def main():
    """Главная функция тестирования."""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ EMAIL УВЕДОМЛЕНИЙ")
    print("=" * 60)
    print(f"\n📋 Конфигурация:")
    print(f"   SMTP сервер: {settings.email_host}:{settings.email_port}")
    print(f"   От кого: {settings.email_from}")
    print(f"   Админ: {settings.email_admin}")
    print(f"   Пользователь: {settings.email_user}")
    print("=" * 60)
    
    # Проверяем наличие пароля
    if not settings.email_password or settings.email_password == "your-email-password-here":
        print("\n❌ ОШИБКА: Не установлен пароль для email!")
        print("   Установите EMAIL_PASSWORD в файле .env")
        return
    
    # Тест 1: Уведомление админу
    result1 = await test_admin_notification()
    
    # Небольшая пауза между отправками
    await asyncio.sleep(2)
    
    # Тест 2: Приветственное письмо
    result2 = await test_welcome_email()
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    print(f"Уведомление админу: {'✅ Успешно' if result1 else '❌ Ошибка'}")
    print(f"Приветственное письмо: {'✅ Успешно' if result2 else '❌ Ошибка'}")
    print("=" * 60)
    
    if result1 and result2:
        print("\n🎉 Все тесты пройдены успешно!")
        print("📬 Проверьте почтовый ящик для подтверждения")
    else:
        print("\n⚠️  Некоторые тесты не прошли. Проверьте логи выше.")


if __name__ == "__main__":
    asyncio.run(main())
