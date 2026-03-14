# 📚 API Документация для фронтенда

**Base URL:** `http://localhost:8000`

**API Key:** `internal-bot-key-2026` (для всех эндпоинтов кроме создания заявки)

---

## 🔐 Аутентификация

Для большинства эндпоинтов требуется API ключ в заголовке:

```javascript
headers: {
  'X-API-Key': 'internal-bot-key-2026'
}
```

**Исключение:** `POST /api/v1/applications/` - не требует API ключ (доступен с фронтенда)

---

## 📝 Applications (Заявки)

### Создать заявку (БЕЗ API ключа)

**Endpoint:** `POST /api/v1/applications/`

**Content-Type:** `multipart/form-data`

**Параметры:**
- `name` (обязательно) - Имя клиента
- `email` (обязательно) - Email клиента
- `message` (обязательно) - Сообщение
- `company` (опционально) - Название компании
- `phone` (опционально) - Телефон
- `file` (опционально) - Прикрепленный файл

**Пример (JavaScript):**
```javascript
const formData = new FormData();
formData.append('name', 'Иван Иванов');
formData.append('email', 'ivan@example.com');
formData.append('message', 'Хочу откликнуться на вакансию');
formData.append('company', 'ООО Компания');
formData.append('phone', '+7 999 123-45-67');
formData.append('file', fileInput.files[0]); // File object

const response = await fetch('http://localhost:8000/api/v1/applications/', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log(data);
```

**Ответ (201):**
```json
{
  "id": 1,
  "name": "Иван Иванов",
  "company": "ООО Компания",
  "email": "ivan@example.com",
  "phone": "+7 999 123-45-67",
  "message": "Хочу откликнуться на вакансию",
  "file_path": "/app/uploads/uuid.pdf",
  "status": "new",
  "created_at": "2026-03-14T12:00:00Z",
  "updated_at": "2026-03-14T12:00:00Z"
}
```

---

### Получить все заявки

**Endpoint:** `GET /api/v1/applications/`

**Headers:** `X-API-Key: internal-bot-key-2026`

**Пример:**
```javascript
const response = await fetch('http://localhost:8000/api/v1/applications/', {
  headers: {
    'X-API-Key': 'internal-bot-key-2026'
  }
});

const applications = await response.json();
```

**Ответ (200):**
```json
[
  {
    "id": 1,
    "name": "Иван Иванов",
    "email": "ivan@example.com",
    "message": "Сообщение",
    "status": "new",
    ...
  }
]
```

---

### Получить заявку по ID

**Endpoint:** `GET /api/v1/applications/{id}`

**Headers:** `X-API-Key: internal-bot-key-2026`

**Пример:**
```javascript
const response = await fetch('http://localhost:8000/api/v1/applications/1', {
  headers: {
    'X-API-Key': 'internal-bot-key-2026'
  }
});

const application = await response.json();
```

---

### Изменить статус заявки

**Endpoint:** `PATCH /api/v1/applications/{id}/status?status={new_status}`

**Headers:** `X-API-Key: internal-bot-key-2026`

**Пример:**
```javascript
const response = await fetch('http://localhost:8000/api/v1/applications/1/status?status=in_progress', {
  method: 'PATCH',
  headers: {
    'X-API-Key': 'internal-bot-key-2026'
  }
});
```

---

### Удалить заявку

**Endpoint:** `DELETE /api/v1/applications/{id}`

**Headers:** `X-API-Key: internal-bot-key-2026`

**Пример:**
```javascript
const response = await fetch('http://localhost:8000/api/v1/applications/1', {
  method: 'DELETE',
  headers: {
    'X-API-Key': 'internal-bot-key-2026'
  }
});
```

---

## 💼 Vacancies (Вакансии)

### Получить все вакансии

**Endpoint:** `GET /api/v1/vacancies/`

**Headers:** `X-API-Key: internal-bot-key-2026`

**Пример:**
```javascript
const response = await fetch('http://localhost:8000/api/v1/vacancies/', {
  headers: {
    'X-API-Key': 'internal-bot-key-2026'
  }
});

const vacancies = await response.json();
```

**Ответ (200):**
```json
[
  {
    "id": 1,
    "title": "Frontend Developer",
    "description": "Описание вакансии",
    "requirements": "Требования",
    "salary": "100000-150000",
    "location": "Москва",
    "is_hidden": false,
    "rating": 0,
    "created_at": "2026-03-14T12:00:00Z",
    "updated_at": "2026-03-14T12:00:00Z"
  }
]
```

---

### Создать вакансию

**Endpoint:** `POST /api/v1/vacancies/`

**Headers:** 
- `X-API-Key: internal-bot-key-2026`
- `Content-Type: application/json`

**Body:**
```json
{
  "title": "Frontend Developer",
  "description": "Описание вакансии",
  "requirements": "Требования",
  "salary": "100000-150000",
  "location": "Москва"
}
```

**Пример:**
```javascript
const response = await fetch('http://localhost:8000/api/v1/vacancies/', {
  method: 'POST',
  headers: {
    'X-API-Key': 'internal-bot-key-2026',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'Frontend Developer',
    description: 'Описание вакансии',
    requirements: 'Требования',
    salary: '100000-150000',
    location: 'Москва'
  })
});
```

---

### Обновить вакансию

**Endpoint:** `PUT /api/v1/vacancies/{id}`

**Headers:** 
- `X-API-Key: internal-bot-key-2026`
- `Content-Type: application/json`

**Body:** (все поля опциональны)
```json
{
  "title": "Senior Frontend Developer",
  "salary": "150000-200000"
}
```

---

### Скрыть/показать вакансию

**Endpoint:** `PATCH /api/v1/vacancies/{id}/hide?is_hidden={true|false}`

**Headers:** `X-API-Key: internal-bot-key-2026`

**Пример:**
```javascript
// Скрыть вакансию
await fetch('http://localhost:8000/api/v1/vacancies/1/hide?is_hidden=true', {
  method: 'PATCH',
  headers: {
    'X-API-Key': 'internal-bot-key-2026'
  }
});
```

---

### Изменить рейтинг вакансии

**Endpoint:** `PATCH /api/v1/vacancies/{id}/rating?rating={number}`

**Headers:** `X-API-Key: internal-bot-key-2026`

**Пример:**
```javascript
await fetch('http://localhost:8000/api/v1/vacancies/1/rating?rating=5', {
  method: 'PATCH',
  headers: {
    'X-API-Key': 'internal-bot-key-2026'
  }
});
```

---

### Удалить вакансию

**Endpoint:** `DELETE /api/v1/vacancies/{id}`

**Headers:** `X-API-Key: internal-bot-key-2026`

---

## ⭐ Reviews (Отзывы)

### Получить все отзывы

**Endpoint:** `GET /api/v1/reviews/`

**Headers:** `X-API-Key: internal-bot-key-2026`

**Ответ:**
```json
[
  {
    "id": 1,
    "author": "Иван Иванов",
    "company": "ООО Компания",
    "position": "CEO",
    "content": "Отличная работа!",
    "rating": 5,
    "is_hidden": false,
    "created_at": "2026-03-14T12:00:00Z",
    "updated_at": "2026-03-14T12:00:00Z"
  }
]
```

---

### Создать отзыв

**Endpoint:** `POST /api/v1/reviews/`

**Headers:** 
- `X-API-Key: internal-bot-key-2026`
- `Content-Type: application/json`

**Body:**
```json
{
  "author": "Иван Иванов",
  "company": "ООО Компания",
  "position": "CEO",
  "content": "Отличная работа!",
  "rating": 5
}
```

---

### Обновить отзыв

**Endpoint:** `PUT /api/v1/reviews/{id}`

**Headers:** 
- `X-API-Key: internal-bot-key-2026`
- `Content-Type: application/json`

---

### Скрыть/показать отзыв

**Endpoint:** `PATCH /api/v1/reviews/{id}/hide?is_hidden={true|false}`

**Headers:** `X-API-Key: internal-bot-key-2026`

---

### Изменить рейтинг отзыва

**Endpoint:** `PATCH /api/v1/reviews/{id}/rating?rating={number}`

**Headers:** `X-API-Key: internal-bot-key-2026`

---

### Удалить отзыв

**Endpoint:** `DELETE /api/v1/reviews/{id}`

**Headers:** `X-API-Key: internal-bot-key-2026`

---

## 📰 Articles (Статьи)

### Получить все статьи

**Endpoint:** `GET /api/v1/articles/`

**Headers:** `X-API-Key: internal-bot-key-2026`

**Ответ:**
```json
[
  {
    "id": 1,
    "title": "Заголовок статьи",
    "content": "Содержание статьи",
    "author": "Автор",
    "is_hidden": false,
    "rating": 0,
    "created_at": "2026-03-14T12:00:00Z",
    "updated_at": "2026-03-14T12:00:00Z"
  }
]
```

---

### Создать статью

**Endpoint:** `POST /api/v1/articles/`

**Headers:** 
- `X-API-Key: internal-bot-key-2026`
- `Content-Type: application/json`

**Body:**
```json
{
  "title": "Заголовок статьи",
  "content": "Содержание статьи",
  "author": "Автор"
}
```

---

### Обновить статью

**Endpoint:** `PUT /api/v1/articles/{id}`

**Headers:** 
- `X-API-Key: internal-bot-key-2026`
- `Content-Type: application/json`

---

### Скрыть/показать статью

**Endpoint:** `PATCH /api/v1/articles/{id}/hide?is_hidden={true|false}`

**Headers:** `X-API-Key: internal-bot-key-2026`

---

### Изменить рейтинг статьи

**Endpoint:** `PATCH /api/v1/articles/{id}/rating?rating={number}`

**Headers:** `X-API-Key: internal-bot-key-2026`

---

### Удалить статью

**Endpoint:** `DELETE /api/v1/articles/{id}`

**Headers:** `X-API-Key: internal-bot-key-2026`

---

## 💼 Cases (Портфолио)

### Получить все кейсы

**Endpoint:** `GET /api/v1/cases/`

**Headers:** `X-API-Key: internal-bot-key-2026`

**Ответ:**
```json
[
  {
    "id": 1,
    "title": "Название проекта",
    "description": "Описание проекта",
    "client": "Клиент",
    "technologies": "React, Node.js",
    "result": "Результат",
    "is_hidden": false,
    "is_fresh": true,
    "rating": 0,
    "created_at": "2026-03-14T12:00:00Z",
    "updated_at": "2026-03-14T12:00:00Z"
  }
]
```

---

### Получить свежие кейсы

**Endpoint:** `GET /api/v1/cases/fresh`

**Headers:** `X-API-Key: internal-bot-key-2026`

**Описание:** Возвращает только кейсы с `is_fresh=true`

---

### Создать кейс

**Endpoint:** `POST /api/v1/cases/`

**Headers:** 
- `X-API-Key: internal-bot-key-2026`
- `Content-Type: application/json`

**Body:**
```json
{
  "title": "Название проекта",
  "description": "Описание проекта",
  "client": "Клиент",
  "technologies": "React, Node.js",
  "result": "Результат"
}
```

---

### Обновить кейс

**Endpoint:** `PUT /api/v1/cases/{id}`

**Headers:** 
- `X-API-Key: internal-bot-key-2026`
- `Content-Type: application/json`

---

### Скрыть/показать кейс

**Endpoint:** `PATCH /api/v1/cases/{id}/hide?is_hidden={true|false}`

**Headers:** `X-API-Key: internal-bot-key-2026`

---

### Отметить кейс как свежий/не свежий

**Endpoint:** `PATCH /api/v1/cases/{id}/fresh?is_fresh={true|false}`

**Headers:** `X-API-Key: internal-bot-key-2026`

---

### Изменить рейтинг кейса

**Endpoint:** `PATCH /api/v1/cases/{id}/rating?rating={number}`

**Headers:** `X-API-Key: internal-bot-key-2026`

---

### Удалить кейс

**Endpoint:** `DELETE /api/v1/cases/{id}`

**Headers:** `X-API-Key: internal-bot-key-2026`

---

## 🔍 Swagger UI

Интерактивная документация доступна по адресу:

**http://localhost:8000/schema/swagger**

В Swagger UI можно:
- Просмотреть все эндпоинты
- Протестировать запросы
- Увидеть примеры ответов
- Загрузить файлы в заявках (кнопка "Choose File")

**Важно:** Для эндпоинтов с API ключом нажмите кнопку "Authorize" и введите: `internal-bot-key-2026`

---

## ❌ Коды ошибок

- `200` - Успешно
- `201` - Создано
- `400` - Ошибка валидации
- `401` - Не авторизован (неверный API ключ)
- `404` - Не найдено
- `500` - Внутренняя ошибка сервера

**Пример ошибки:**
```json
{
  "status_code": 400,
  "detail": "Ошибка валидации"
}
```

---

## 📦 Полный пример React компонента

```javascript
import React, { useState } from 'react';

function ApplicationForm() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: '',
    company: '',
    phone: ''
  });
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const data = new FormData();
    data.append('name', formData.name);
    data.append('email', formData.email);
    data.append('message', formData.message);
    if (formData.company) data.append('company', formData.company);
    if (formData.phone) data.append('phone', formData.phone);
    if (file) data.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/v1/applications/', {
        method: 'POST',
        body: data
      });

      if (response.ok) {
        const result = await response.json();
        alert('Заявка отправлена! ID: ' + result.id);
        // Очистить форму
        setFormData({ name: '', email: '', message: '', company: '', phone: '' });
        setFile(null);
      } else {
        alert('Ошибка отправки заявки');
      }
    } catch (error) {
      console.error('Ошибка:', error);
      alert('Ошибка сети');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Имя *"
        value={formData.name}
        onChange={(e) => setFormData({...formData, name: e.target.value})}
        required
      />
      <input
        type="email"
        placeholder="Email *"
        value={formData.email}
        onChange={(e) => setFormData({...formData, email: e.target.value})}
        required
      />
      <textarea
        placeholder="Сообщение *"
        value={formData.message}
        onChange={(e) => setFormData({...formData, message: e.target.value})}
        required
      />
      <input
        type="text"
        placeholder="Компания"
        value={formData.company}
        onChange={(e) => setFormData({...formData, company: e.target.value})}
      />
      <input
        type="tel"
        placeholder="Телефон"
        value={formData.phone}
        onChange={(e) => setFormData({...formData, phone: e.target.value})}
      />
      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Отправка...' : 'Отправить'}
      </button>
    </form>
  );
}

export default ApplicationForm;
```

---

## 🎯 Итог

Все готово для интеграции с фронтендом! Используйте эту документацию для подключения API к вашему сайту.
