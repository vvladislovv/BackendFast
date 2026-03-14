#!/bin/bash
# Быстрое тестирование API

API_KEY="internal-bot-key-2026"
BASE_URL="http://localhost:8000"

echo "🚀 Быстрое тестирование API"
echo "================================"

# Проверка что API работает
echo -e "\n✅ Проверка доступности API..."
curl -s $BASE_URL/health | jq '.'

# Тест без API ключа (должен вернуть 401)
echo -e "\n❌ Тест БЕЗ API ключа (ожидается 401)..."
curl -s $BASE_URL/api/v1/vacancies | jq '.'

# Тест с API ключом
echo -e "\n✅ Тест С API ключом..."
curl -s -H "X-API-Key: $API_KEY" $BASE_URL/api/v1/vacancies | jq '.'

# Создание вакансии
echo -e "\n✅ Создание вакансии..."
curl -s -X POST $BASE_URL/api/v1/vacancies \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Vacancy",
    "description": "Test description",
    "requirements": "Test requirements",
    "salary": "100000",
    "location": "Moscow",
    "employment_type": "full_time"
  }' | jq '.'

# Создание заявки БЕЗ API ключа
echo -e "\n✅ Создание заявки БЕЗ API ключа..."
curl -s -X POST $BASE_URL/api/v1/applications \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "phone": "+79991234567",
    "message": "Test message"
  }' | jq '.'

echo -e "\n================================"
echo "✅ Тестирование завершено!"
echo "Для полного тестирования запустите: python scripts/test_api.py"
