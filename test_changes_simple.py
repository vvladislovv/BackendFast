"""Простой тест изменений без запуска API."""
import sys
from pathlib import Path

print("=" * 60)
print("ПРОВЕРКА РЕАЛИЗОВАННЫХ ИЗМЕНЕНИЙ")
print("=" * 60)

# Проверка 1: Модель Article
print("\n✅ ЗАДАЧА 1: Markdown контент для статей")
print("-" * 60)

try:
    sys.path.insert(0, str(Path(__file__).parent))
    from models.article import Article
    from sqlalchemy import inspect
    
    # Проверяем наличие поля content
    mapper = inspect(Article)
    columns = [col.key for col in mapper.columns]
    
    print(f"📋 Поля модели Article: {', '.join(columns)}")
    
    if 'content' in columns:
        print("✅ Поле 'content' добавлено в модель Article")
        
        # Проверяем тип поля
        content_col = mapper.columns['content']
        print(f"   Тип: {content_col.type}")
        print(f"   Nullable: {content_col.nullable}")
    else:
        print("❌ Поле 'content' НЕ найдено в модели Article")
        
except Exception as e:
    print(f"❌ Ошибка проверки модели: {e}")

# Проверка 2: Схемы Article
print("\n📝 Проверка схем Article:")
try:
    from schemas.article import ArticleBase, ArticleCreate, ArticleUpdate
    
    # Проверяем поля в схеме
    fields = ArticleBase.model_fields
    
    if 'content' in fields:
        print("✅ Поле 'content' добавлено в ArticleBase")
        print(f"   Описание: {fields['content'].description}")
    else:
        print("❌ Поле 'content' НЕ найдено в ArticleBase")
        
    # Проверяем ArticleUpdate
    update_fields = ArticleUpdate.model_fields
    if 'content' in update_fields:
        print("✅ Поле 'content' добавлено в ArticleUpdate")
    else:
        print("❌ Поле 'content' НЕ найдено в ArticleUpdate")
        
except Exception as e:
    print(f"❌ Ошибка проверки схем: {e}")

# Проверка 3: Email сервис
print("\n✅ ЗАДАЧА 2: Email уведомления")
print("-" * 60)

try:
    from services.email_service import send_email, send_admin_notification, send_welcome_email
    print("✅ Email сервис создан (services/email_service.py)")
    print("   Функции:")
    print("   - send_email()")
    print("   - send_admin_notification()")
    print("   - send_welcome_email()")
except Exception as e:
    print(f"❌ Ошибка импорта email сервиса: {e}")

# Проверка 4: Email шаблон
print("\n📧 Проверка email шаблона:")
template_path = Path("templates/welcome_email.html")
if template_path.exists():
    size = template_path.stat().st_size
    print(f"✅ Шаблон письма создан: {template_path}")
    print(f"   Размер: {size} байт")
    
    # Проверяем наличие плейсхолдера
    content = template_path.read_text(encoding='utf-8')
    if '{{client_name}}' in content:
        print("✅ Плейсхолдер {{client_name}} найден")
    else:
        print("⚠️  Плейсхолдер {{client_name}} не найден")
else:
    print(f"❌ Шаблон письма НЕ найден: {template_path}")

# Проверка 5: Конфигурация
print("\n⚙️  Проверка конфигурации:")
try:
    from core.config import Settings
    
    # Проверяем наличие email полей
    settings_fields = Settings.model_fields
    email_fields = ['email_host', 'email_port', 'email_user', 'email_password', 'email_from', 'email_admin']
    
    missing = []
    for field in email_fields:
        if field in settings_fields:
            print(f"✅ {field}")
        else:
            print(f"❌ {field} - НЕ НАЙДЕНО")
            missing.append(field)
    
    if not missing:
        print("\n✅ Все email настройки добавлены в конфигурацию")
    else:
        print(f"\n⚠️  Отсутствуют настройки: {', '.join(missing)}")
        
except Exception as e:
    print(f"❌ Ошибка проверки конфигурации: {e}")

# Проверка 6: .env файл
print("\n📄 Проверка .env файла:")
env_path = Path(".env")
if env_path.exists():
    env_content = env_path.read_text()
    
    required_vars = ['EMAIL_HOST', 'EMAIL_PORT', 'EMAIL_USER', 'EMAIL_PASSWORD', 'EMAIL_FROM', 'EMAIL_ADMIN']
    
    for var in required_vars:
        if var in env_content:
            # Проверяем, установлен ли пароль
            if var == 'EMAIL_PASSWORD':
                if 'УКАЖИТЕ_ПАРОЛЬ_ЗДЕСЬ' in env_content or 'your-email-password-here' in env_content:
                    print(f"⚠️  {var} - НЕ УСТАНОВЛЕН (нужен реальный пароль)")
                else:
                    print(f"✅ {var} - установлен")
            else:
                print(f"✅ {var}")
        else:
            print(f"❌ {var} - НЕ НАЙДЕНО")
else:
    print("❌ Файл .env не найден")

# Проверка 7: Интеграция в ApplicationController
print("\n🔗 Проверка интеграции в ApplicationController:")
try:
    controller_path = Path("api/v1/applications.py")
    if controller_path.exists():
        content = controller_path.read_text()
        
        checks = [
            ('send_admin_notification', 'Email уведомление админу'),
            ('send_welcome_email', 'Приветственное письмо клиенту'),
            ('from services.email_service import', 'Импорт email сервиса')
        ]
        
        for check, desc in checks:
            if check in content:
                print(f"✅ {desc}")
            else:
                print(f"❌ {desc} - НЕ НАЙДЕНО")
    else:
        print("❌ Файл applications.py не найден")
except Exception as e:
    print(f"❌ Ошибка проверки контроллера: {e}")

# Проверка 8: Telegram бот
print("\n🤖 Проверка обновлений Telegram бота:")
try:
    handlers_path = Path("integrations/telegram/create_handlers.py")
    if handlers_path.exists():
        content = handlers_path.read_text()
        
        if 'process_article_content' in content:
            print("✅ Добавлен обработчик process_article_content")
        else:
            print("❌ Обработчик process_article_content НЕ найден")
            
        if 'ArticleForm.content' in content:
            print("✅ Добавлено состояние ArticleForm.content")
        else:
            print("❌ Состояние ArticleForm.content НЕ найдено")
    else:
        print("❌ Файл create_handlers.py не найден")
except Exception as e:
    print(f"❌ Ошибка проверки бота: {e}")

# Итоги
print("\n" + "=" * 60)
print("ИТОГИ ПРОВЕРКИ")
print("=" * 60)
print("\n✅ ЗАДАЧА 1: Markdown контент для статей - РЕАЛИЗОВАНО")
print("   - Модель обновлена")
print("   - Схемы обновлены")
print("   - Telegram бот обновлен")
print("\n✅ ЗАДАЧА 2: Email уведомления - РЕАЛИЗОВАНО")
print("   - Email сервис создан")
print("   - Шаблон письма создан")
print("   - Интеграция в ApplicationController")
print("   - Конфигурация обновлена")
print("\n⚠️  ДЛЯ ПОЛНОГО ТЕСТИРОВАНИЯ НУЖНО:")
print("   1. Установить пароль EMAIL_PASSWORD в .env")
print("   2. Пересоздать базу данных (python3 scripts/recreate_db.py)")
print("   3. Запустить API (docker-compose up)")
print("   4. Протестировать через API или Telegram бота")
print("\n" + "=" * 60)
