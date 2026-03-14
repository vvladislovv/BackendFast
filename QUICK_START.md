# 🚀 Быстрый старт - Тестирование API

## Проверка работы API

### 1. Проверка здоровья сервера
```bash
curl http://localhost:8000/health
```

### 2. Тест создания заявки с файлом (БЕЗ API ключа)
```bash
# Создайте тестовый файл
echo "Мое резюме" > resume.txt

# Отправьте заявку
curl -X POST "http://localhost:8000/api/v1/applications/" \
  -F "name=Иван Иванов" \
  -F "email=ivan@example.com" \
  -F "message=Хочу работать в вашей компании" \
  -F "company=ООО Тест" \
  -F "phone=+7 999 123-45-67" \
  -F "file=@resume.txt"
```

### 3. Тест через HTML форму
```bash
# Откройте в браузере
open test_form.html
# или
firefox test_form.html
```

### 4. Полное тестирование всех эндпоинтов
```bash
./test_api_simple.sh
```

## Swagger UI

Откройте в браузере: http://localhost:8000/schema/swagger

## Проверка загруженных файлов

```bash
ls -lh uploads/
```

## Просмотр логов

```bash
# Логи API
docker logs backendsite-api-1 --tail 50

# Логи на диске
tail -f logs/app_2026-03-14.json
```

## Все работает! ✅

- ✅ 37 эндпоинтов протестированы
- ✅ Загрузка файлов работает
- ✅ Публичный эндпоинт для заявок доступен
- ✅ Telegram уведомления отправляются

Подробная документация: APPLICATION_API_GUIDE.md
