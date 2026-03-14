# ✅ SWAGGER UI - ПОЛНАЯ ИНСТРУКЦИЯ

## 🎯 Быстрый старт

1. Откройте Swagger UI: http://localhost:8000/schema/swagger
2. Обновите страницу с очисткой кэша: **Cmd+Shift+R** (Mac) или **Ctrl+Shift+R** (Windows)
3. Найдите раздел **Applications**
4. Откройте **POST /api/v1/applications/**

---

## 📝 Тест БЕЗ файла (простой)

### В Swagger UI:

1. Нажмите **"Try it out"**
2. Вставьте JSON:

```json
{
  "name": "Иван Иванов",
  "email": "ivan@example.com",
  "message": "Хочу откликнуться на вакансию",
  "company": "ООО Тест",
  "phone": "+7 999 123-45-67"
}
```

3. Нажмите **"Execute"**

### Ожидаемый результат:
- ✅ Статус: **201 Created**
- ✅ `file_path: null` (файла нет)
- ✅ `status: "new"`

---

## 📎 Тест С ФАЙЛОМ (через base64)

### Способ 1: Swagger UI с base64

1. Конвертируйте файл в base64:
   - Онлайн: https://base64.guru/converter/encode/file
   - Или используйте команду: `base64 -i your_file.pdf`

2. В Swagger UI вставьте JSON:

```json
{
  "name": "Иван Иванов",
  "email": "ivan@example.com",
  "message": "Хочу откликнуться на вакансию",
  "company": "ООО Тест",
  "phone": "+7 999 123-45-67",
  "file_base64": "JVBERi0xLjQKJeLjz9MKMSAwIG9iago8PC9UeXBlL...",
  "file_name": "resume.pdf"
}
```

3. Нажмите **"Execute"**

### Ожидаемый результат:
- ✅ Статус: **201 Created**
- ✅ `file_path: "/app/uploads/UUID.pdf"` (файл сохранен!)
- ✅ Файл доступен на сервере

---

## 🌐 Способ 2: HTML форма (автоматическая конвертация)

Откройте в браузере: **file:///path/to/test_form_base64.html**

Эта форма автоматически:
- Конвертирует файл в base64
- Отправляет JSON запрос
- Показывает результат

**Преимущества:**
- Не нужно вручную конвертировать файл
- Удобный интерфейс
- Показывает размер и тип файла

---

## 🔧 Способ 3: curl с multipart (для больших файлов)

Для больших файлов используйте эндпоинт `/upload`:

```bash
curl -X POST "http://localhost:8000/api/v1/applications/upload" \
  -F "name=Иван Иванов" \
  -F "email=ivan@example.com" \
  -F "message=Хочу заказать разработку сайта" \
  -F "company=ООО Компания" \
  -F "phone=+7 999 123-45-67" \
  -F "file=@resume.pdf"
```

**Когда использовать:**
- Файлы больше 5 MB
- Автоматизация через скрипты
- Интеграция с другими системами

---

## 📊 Проверка загруженных файлов

```bash
# Посмотреть все файлы
ls -lh uploads/

# Посмотреть содержимое текстового файла
cat uploads/UUID.txt

# Открыть PDF
open uploads/UUID.pdf  # Mac
xdg-open uploads/UUID.pdf  # Linux
```

---

## 🤖 Интеграция с Telegram ботом

После создания заявки:
1. ✅ Заявка сохраняется в БД
2. ✅ Файл сохраняется в `/app/uploads/`
3. ✅ Отправляется уведомление в Telegram бот
4. ✅ Бот получает путь к файлу и может его отправить

---

## 🎨 Примеры для разных языков

### JavaScript (браузер):
```javascript
const file = document.getElementById('fileInput').files[0];
const reader = new FileReader();
reader.onload = async () => {
  const base64 = reader.result.split(',')[1];
  
  const response = await fetch('http://localhost:8000/api/v1/applications/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: "Иван",
      email: "ivan@example.com",
      message: "Тест",
      file_base64: base64,
      file_name: file.name
    })
  });
  
  const data = await response.json();
  console.log('Заявка создана:', data);
};
reader.readAsDataURL(file);
```

### Python:
```python
import base64
import requests

# Читаем файл
with open('resume.pdf', 'rb') as f:
    file_content = f.read()
    file_base64 = base64.b64encode(file_content).decode()

# Отправляем запрос
response = requests.post('http://localhost:8000/api/v1/applications/', json={
    'name': 'Иван Иванов',
    'email': 'ivan@example.com',
    'message': 'Хочу откликнуться',
    'file_base64': file_base64,
    'file_name': 'resume.pdf'
})

print(response.json())
```

### curl с base64:
```bash
# Конвертируем файл
FILE_BASE64=$(base64 -i resume.pdf)

# Отправляем
curl -X POST "http://localhost:8000/api/v1/applications/" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Иван Иванов\",
    \"email\": \"ivan@example.com\",
    \"message\": \"Тест\",
    \"file_base64\": \"$FILE_BASE64\",
    \"file_name\": \"resume.pdf\"
  }"
```

---

## ⚠️ Ограничения base64

**Плюсы:**
- ✅ Работает в Swagger UI
- ✅ Работает через JSON API
- ✅ Простая интеграция

**Минусы:**
- ❌ Увеличивает размер на ~33%
- ❌ Не подходит для файлов > 10 MB
- ❌ Больше нагрузка на память

**Рекомендация:**
- Для файлов < 5 MB: используйте base64 (Swagger UI)
- Для файлов > 5 MB: используйте `/upload` (multipart)

---

## 🎉 Все работает!

- ✅ JSON запросы в Swagger UI
- ✅ Загрузка файлов через base64
- ✅ Загрузка файлов через multipart
- ✅ Валидация данных
- ✅ Сохранение файлов на сервере
- ✅ Уведомления в Telegram
- ✅ HTML форма для удобного тестирования
