# ⚠️ Ограничение Swagger UI для загрузки файлов

## Проблема

Litestar (библиотека для API) не генерирует правильную OpenAPI схему для `multipart/form-data` с файлами в Swagger UI. Это известное ограничение библиотеки.

**Что не работает в Swagger UI:**
- ❌ Кнопка "Choose File" для загрузки файла
- ❌ Поля отображаются как query параметры вместо form-data

## ✅ Рабочие решения

### 1. HTML форма (РЕКОМЕНДУЕТСЯ для тестирования)

Откройте файл `test_form.html` в браузере:

```bash
open test_form.html  # Mac
xdg-open test_form.html  # Linux
start test_form.html  # Windows
```

**Преимущества:**
- ✅ Удобный интерфейс
- ✅ Выбор файла через кнопку
- ✅ Показывает результат сразу
- ✅ Работает локально без установки

### 2. curl (для автоматизации)

```bash
curl -X POST "http://localhost:8000/api/v1/applications/" \
  -F "name=Иван Иванов" \
  -F "email=ivan@example.com" \
  -F "message=Хочу откликнуться на вакансию" \
  -F "company=ООО Компания" \
  -F "phone=+7 999 123-45-67" \
  -F "file=@resume.pdf"
```

**Преимущества:**
- ✅ Быстро
- ✅ Можно автоматизировать
- ✅ Работает в скриптах

### 3. Postman / Insomnia

1. Создайте POST запрос на `http://localhost:8000/api/v1/applications/`
2. Выберите Body → form-data
3. Добавьте поля: name, email, message, company, phone
4. Для file выберите тип "File" и загрузите файл
5. Отправьте запрос

**Преимущества:**
- ✅ Графический интерфейс
- ✅ Сохранение запросов
- ✅ История запросов

## 📝 Что можно тестировать в Swagger UI

В Swagger UI можно тестировать ВСЕ остальные эндпоинты:

- ✅ GET /api/v1/applications/ - получить все заявки
- ✅ GET /api/v1/applications/{id} - получить заявку по ID
- ✅ PATCH /api/v1/applications/{id}/status - изменить статус
- ✅ DELETE /api/v1/applications/{id} - удалить заявку
- ✅ Все эндпоинты Articles, Cases, Reviews, Vacancies

**Для этих эндпоинтов нужен API ключ:** `internal-bot-key-2026`

## 🔧 Техническая информация

**Почему не работает:**

Litestar генерирует параметры с `Body(media_type=RequestEncodingType.MULTI_PART)` как query параметры в OpenAPI схеме вместо requestBody с multipart/form-data.

**Пример неправильной схемы:**
```json
{
  "parameters": [
    {
      "name": "file",
      "in": "query",  // ❌ Должно быть в requestBody
      "schema": {
        "type": "string",
        "format": "binary"
      }
    }
  ]
}
```

**Правильная схема должна быть:**
```json
{
  "requestBody": {
    "content": {
      "multipart/form-data": {
        "schema": {
          "type": "object",
          "properties": {
            "file": {
              "type": "string",
              "format": "binary"
            }
          }
        }
      }
    }
  }
}
```

## 📚 Альтернативные решения (не реализованы)

1. **Два отдельных эндпоинта:**
   - POST /api/v1/applications/ - JSON без файла (работает в Swagger)
   - POST /api/v1/applications/upload - multipart с файлом (только curl)

2. **Base64 в JSON:**
   - Файл кодируется в base64 строку
   - Отправляется как обычный JSON
   - ❌ Увеличивает размер на 33%
   - ❌ Не подходит для больших файлов

3. **Кастомная OpenAPI схема:**
   - Вручную переопределить схему
   - ❌ Сложно поддерживать
   - ❌ Может сломаться при обновлении Litestar

## ✅ Итог

**Для тестирования с файлами используйте:**
1. HTML форму `test_form.html` (самый удобный способ)
2. curl команды
3. Postman/Insomnia

**Swagger UI используйте для:**
- Всех остальных эндпоинтов без файлов
- Просмотра документации API
- Быстрого тестирования GET/PATCH/DELETE запросов

Все работает корректно, просто Swagger UI не подходит для загрузки файлов в Litestar!
