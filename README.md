# Backend API на Litestar

Современный высокопроизводительный backend на Python 3.13 с использованием Litestar framework, PostgreSQL и Telegram Bot.

## Технологии

- **Python 3.13** - стабильная версия
- **Litestar 2.12.1** - современный ASGI framework
- **PostgreSQL** - база данных
- **SQLAlchemy 2.0** - async ORM
- **Pydantic v2** - валидация данных
- **Loguru** - логирование
- **Aiogram 3.x** - Telegram bot
- **Alembic** - миграции БД
- **pytest** - тестирование
- **Docker** - контейнеризация

## Быстрый старт

### Вариант 1: Docker (рекомендуется)

```bash
# 1. Создать .env файл
cp .env.example .env
# Отредактировать .env (добавить токены)

# 2. Запустить все сервисы
docker-compose up -d

# 3. Проверить
curl http://localhost:8000/health
```

### Вариант 2: Локально

```bash
# 1. Создать виртуальное окружение
python3.13 -m venv venv
source venv/bin/activate

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Настроить .env
cp .env.example .env
python scripts/generate_secret.py

# 4. Применить миграции
alembic upgrade head

# 5. Запустить
python main.py
```

## Структура проекта

```
backend/
├── core/              # Конфигурация, БД, безопасность
├── models/            # ORM модели
├── schemas/           # Pydantic схемы
├── services/          # Бизнес-логика
├── api/               # API endpoints
├── middleware/        # Обработка ошибок
├── integrations/      # Telegram bot
├── utils/             # Утилиты
├── tests/             # Тесты
├── alembic/           # Миграции
└── main.py            # Точка входа
```

## API Endpoints

### Вакансии
- `POST /api/v1/vacancies` - создать
- `GET /api/v1/vacancies` - получить все
- `GET /api/v1/vacancies/{id}` - получить по ID
- `PUT /api/v1/vacancies/{id}` - обновить
- `DELETE /api/v1/vacancies/{id}` - удалить
- `PATCH /api/v1/vacancies/{id}/hide` - скрыть/показать
- `PATCH /api/v1/vacancies/{id}/rating` - изменить рейтинг

### Отзывы
- `POST /api/v1/reviews` - создать
- `GET /api/v1/reviews` - получить все
- `GET /api/v1/reviews/{id}` - получить по ID
- `PUT /api/v1/reviews/{id}` - обновить
- `DELETE /api/v1/reviews/{id}` - удалить
- `PATCH /api/v1/reviews/{id}/hide` - скрыть/показать
- `PATCH /api/v1/reviews/{id}/rating` - изменить рейтинг

### Статьи
- `POST /api/v1/articles` - создать
- `GET /api/v1/articles` - получить все
- `GET /api/v1/articles/{id}` - получить по ID
- `PUT /api/v1/articles/{id}` - обновить
- `DELETE /api/v1/articles/{id}` - удалить
- `PATCH /api/v1/articles/{id}/hide` - скрыть/показать
- `PATCH /api/v1/articles/{id}/rating` - изменить рейтинг

### Кейсы
- `POST /api/v1/cases` - создать
- `GET /api/v1/cases` - получить все
- `GET /api/v1/cases/fresh` - получить свежие
- `GET /api/v1/cases/{id}` - получить по ID
- `PUT /api/v1/cases/{id}` - обновить
- `DELETE /api/v1/cases/{id}` - удалить
- `PATCH /api/v1/cases/{id}/hide` - скрыть/показать
- `PATCH /api/v1/cases/{id}/rating` - изменить рейтинг
- `PATCH /api/v1/cases/{id}/fresh` - пометить как свежий

## Документация API

После запуска доступна по адресам:
- **Swagger UI:** http://localhost:8000/schema/swagger
- **ReDoc:** http://localhost:8000/schema/redoc
- **Health Check:** http://localhost:8000/health

## Настройка .env

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/backend_db

# Security
SECRET_KEY=your-secret-key-here-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_ADMIN_IDS=your_telegram_id

# Application
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_ROTATION=10 MB
LOG_RETENTION=30 days
```

## Telegram Bot

1. Создать бота через @BotFather
2. Получить токен
3. Узнать свой ID через @userinfobot
4. Добавить в .env
5. Запустить: `python integrations/telegram/bot.py`

## Тестирование

```bash
# Создать тестовую БД
createdb test_db

# Запустить тесты
pytest

# С покрытием
pytest --cov=. --cov-report=html
```

## Полезные команды

```bash
# Makefile команды
make help          # Показать все команды
make docker-up     # Запустить Docker
make test          # Запустить тесты
make clean         # Очистить временные файлы

# Docker команды
docker-compose up -d              # Запустить
docker-compose logs -f            # Логи
docker-compose down               # Остановить

# Миграции
alembic upgrade head              # Применить
alembic revision --autogenerate   # Создать
```

## Безопасность

- Валидация всех данных через Pydantic
- Защита от SQL injection через ORM
- JWT токены для авторизации
- Хеширование паролей через bcrypt
- Проверка прав администратора в боте
- Структурированное логирование

## Логирование

Логи сохраняются в папке `logs/`:
- `app_*.json` - все логи в JSON формате
- `errors_*.log` - только ошибки

## Лицензия

MIT License
