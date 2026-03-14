# Backend API - Управление контентом

REST API для управления вакансиями, отзывами, статьями и кейсами.

## Запуск

```bash
docker-compose up -d
```

## Тестирование

```bash
python scripts/test_api.py
```

## API ключ

**Ключ:** `internal-bot-key-2026`  
**Заголовок:** `X-API-Key`

```bash
curl -H "X-API-Key: internal-bot-key-2026" http://localhost:8000/api/v1/vacancies
```

## Swagger

http://localhost:8000/schema/swagger

## Документация

[API.md](API.md) - полная документация с примерами

## Технологии

- **Framework**: Litestar 2.12.1
- **Database**: PostgreSQL + SQLAlchemy (async)
- **Validation**: Pydantic
- **Logging**: Loguru
- **Testing**: Pytest
- **Bot**: Telegram (aiogram)
- **Python**: 3.13

## 📚 Документация

### Swagger UI
Интерактивная документация: **http://localhost:8000/schema/swagger**

**⚠️ Важно:** Для тестирования через Swagger UI нужно вручную добавлять заголовок `X-API-Key` в каждом запросе.  
Подробная инструкция: **[SWAGGER_USAGE.md](SWAGGER_USAGE.md)**

### Тестирование API
Подробные инструкции по тестированию API с примерами: **[API_TESTING.md](API_TESTING.md)**

**API Key для тестирования:** `internal-bot-key-2026`

### Endpoints

#### Health
- `GET /health` - Проверка здоровья API
- `GET /` - Информация об API

#### Вакансии
- `POST /api/v1/vacancies` - Создать вакансию
- `GET /api/v1/vacancies` - Получить все вакансии
- `GET /api/v1/vacancies/{id}` - Получить вакансию
- `PUT /api/v1/vacancies/{id}` - Обновить вакансию
- `PATCH /api/v1/vacancies/{id}/rating` - Изменить рейтинг
- `PATCH /api/v1/vacancies/{id}/hide` - Скрыть/показать
- `DELETE /api/v1/vacancies/{id}` - Удалить вакансию

#### Отзывы
- `POST /api/v1/reviews` - Создать отзыв
- `GET /api/v1/reviews` - Получить все отзывы
- `GET /api/v1/reviews/{id}` - Получить отзыв
- `PUT /api/v1/reviews/{id}` - Обновить отзыв
- `PATCH /api/v1/reviews/{id}/rating` - Изменить рейтинг
- `PATCH /api/v1/reviews/{id}/hide` - Скрыть/показать
- `DELETE /api/v1/reviews/{id}` - Удалить отзыв

#### Статьи
- `POST /api/v1/articles` - Создать статью
- `GET /api/v1/articles` - Получить все статьи
- `GET /api/v1/articles/{id}` - Получить статью
- `PUT /api/v1/articles/{id}` - Обновить статью
- `PATCH /api/v1/articles/{id}/rating` - Изменить рейтинг
- `PATCH /api/v1/articles/{id}/hide` - Скрыть/показать
- `DELETE /api/v1/articles/{id}` - Удалить статью

#### Кейсы
- `POST /api/v1/cases` - Создать кейс
- `GET /api/v1/cases` - Получить все кейсы
- `GET /api/v1/cases/fresh` - Получить свежие кейсы
- `GET /api/v1/cases/{id}` - Получить кейс
- `PUT /api/v1/cases/{id}` - Обновить кейс
- `PATCH /api/v1/cases/{id}/rating` - Изменить рейтинг
- `PATCH /api/v1/cases/{id}/fresh` - Пометить как свежий
- `PATCH /api/v1/cases/{id}/hide` - Скрыть/показать
- `DELETE /api/v1/cases/{id}` - Удалить кейс

## 🧪 Тестирование

### Автоматическое тестирование
```bash
./test_all_api.sh
```

### Результаты
- ✅ **32/32 тестов пройдено**
- ✅ **100% успех**
- Подробности в `TEST_RESULTS.md`

## 🔐 Защита API

API защищен через API ключи. Все endpoints (кроме `/health` и Swagger UI) требуют заголовок `X-API-Key`.

### API ключи:
- `settings.secret_key` - основной ключ из .env
- `internal-bot-key-2026` - ключ для Telegram бота

### Пример запроса с ключом:
```bash
curl -H "X-API-Key: your-secret-key" http://localhost:8000/api/v1/vacancies
```

Без ключа возвращается `401 Unauthorized`.

## 🤖 Telegram Bot

Bot ID: `8318949552`
Admin ID: `7718206984`

### Полный функционал:
- ✅ Просмотр списков всех сущностей
- ✅ Создание записей (пошаговое FSM)
- ✅ Поиск по ID
- ✅ Обновление любых полей
- ✅ Изменение рейтинга
- ✅ Скрытие/показ записей
- ✅ Удаление записей
- ✅ Свежие кейсы
- ✅ Пометка кейсов свежими

### Команды:
- `/start` - Главное меню с кнопками
- `/help` - Подробная справка

### Использование:
1. Отправьте `/start` боту
2. Выберите раздел (Вакансии, Отзывы, Статьи, Кейсы)
3. Выберите действие (Список, Создать, Найти, Обновить и т.д.)
4. Следуйте инструкциям бота

Подробная инструкция в `promt/TASKS_COMPLETED.md`

## 🔒 Безопасность

- ✅ **API защищен через API ключи** (401 без ключа)
- ✅ Защита от SQL Injection (SQLAlchemy ORM)
- ✅ Валидация всех входных данных (Pydantic)
- ✅ Типизация полей с ограничениями
- ✅ Ограничения длины строк (title: 1-255, url: 1-500)
- ✅ Валидация диапазонов (stars: 1-5, rating: >= 0)
- ✅ Подробное логирование всех операций
- ✅ Telegram бот доступен только админу

## 📊 Логирование

Логи сохраняются в папке `logs/`:
- `app_YYYY-MM-DD.json` - Все логи в JSON формате
- `errors_YYYY-MM-DD.log` - Только ошибки

Просмотр логов:
```bash
# API
docker logs backendsite-api-1 --tail 50

# Bot
docker logs backendsite-bot-1 --tail 50

# Database
docker logs backendsite-db-1 --tail 50
```

## 🛠️ Управление

### Запуск
```bash
docker-compose up -d
```

### Остановка
```bash
docker-compose down
```

### Перезапуск
```bash
docker-compose restart
```

### Пересборка
```bash
docker-compose down
docker-compose up -d --build
```

### Очистка данных
```bash
docker-compose down -v
```

## 📁 Структура проекта

```
.
├── api/                    # API endpoints
│   ├── health.py          # Health checks
│   └── v1/                # API v1
│       ├── vacancies.py   # Вакансии
│       ├── reviews.py     # Отзывы
│       ├── articles.py    # Статьи
│       └── cases.py       # Кейсы
├── core/                  # Ядро приложения
│   ├── config.py         # Конфигурация
│   ├── database.py       # База данных
│   └── security.py       # Безопасность
├── models/               # SQLAlchemy модели
├── schemas/              # Pydantic схемы
├── services/             # Бизнес-логика
├── middleware/           # Middleware
├── integrations/         # Интеграции
│   └── telegram/        # Telegram бот
├── utils/               # Утилиты
├── tests/               # Тесты
├── main.py              # Точка входа
└── docker-compose.yml   # Docker конфигурация
```

## 🌐 Доступ

- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/schema/swagger
- **Health Check**: http://localhost:8000/health
- **Database**: localhost:5432

## 📝 Примеры использования

### Создание вакансии
```bash
curl -X POST http://localhost:8000/api/v1/vacancies \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{
    "title": "Python Developer",
    "url": "https://example.com/job",
    "employment_type": "Full-time",
    "description": "Great opportunity"
  }'
```

### Получение всех вакансий
```bash
curl -H "X-API-Key: your-secret-key" http://localhost:8000/api/v1/vacancies
```

### Создание отзыва
```bash
curl -X POST http://localhost:8000/api/v1/reviews \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-secret-key" \
  -d '{
    "name": "John Doe",
    "company": "Tech Corp",
    "review": "Excellent service!",
    "stars": 5,
    "photo": "/images/john.jpg"
  }'
```

## 🎯 Статус проекта

✅ Все функции реализованы
✅ Все тесты пройдены (32/32 - 100%)
✅ API защищен через API ключи
✅ Документация создана (Swagger UI)
✅ Telegram бот с полным функционалом
✅ Логирование настроено
✅ Безопасность обеспечена (SQL Injection, XSS, валидация)

**Проект готов к использованию!**

Подробный отчет о выполненных задачах: `promt/TASKS_COMPLETED.md`

## 📄 Лицензия

MIT License

## 👨‍💻 Разработка

Python 3.13 | Litestar | PostgreSQL | Docker
