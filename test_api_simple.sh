#!/bin/bash

# Упрощенное тестирование API с правильным парсингом для macOS

BASE_URL="http://localhost:8000"
API_KEY="internal-bot-key-2026"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}ПОЛНОЕ ТЕСТИРОВАНИЕ API${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Health Check
echo -e "${BLUE}=== HEALTH CHECK ===${NC}"
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""

# ============================================================================
# ARTICLES
# ============================================================================
echo -e "\n${BLUE}=== ТЕСТИРОВАНИЕ ARTICLES ===${NC}\n"

echo -e "${YELLOW}1. Создание статьи...${NC}"
article_response=$(curl -s -X POST "$BASE_URL/api/v1/articles/" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "title": "Тестовая статья",
        "url": "https://example.com/test-article",
        "photo": "/images/test-article.jpg"
    }')
echo "$article_response" | python3 -m json.tool
article_id=$(echo "$article_response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
echo -e "${GREEN}Создана статья ID: $article_id${NC}\n"

echo -e "${YELLOW}2. Получение списка статей...${NC}"
curl -s "$BASE_URL/api/v1/articles/" -H "X-API-Key: $API_KEY" | python3 -m json.tool | head -20
echo ""

echo -e "${YELLOW}3. Получение статьи ID=$article_id...${NC}"
curl -s "$BASE_URL/api/v1/articles/$article_id" -H "X-API-Key: $API_KEY" | python3 -m json.tool
echo ""

echo -e "${YELLOW}4. Обновление статьи...${NC}"
curl -s -X PUT "$BASE_URL/api/v1/articles/$article_id" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"title": "Обновленная статья", "url": "https://example.com/updated-article"}' | python3 -m json.tool
echo ""

echo -e "${YELLOW}5. Повышение рейтинга до 10...${NC}"
curl -s -X PATCH "$BASE_URL/api/v1/articles/$article_id/rating" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"rating": 10}' | python3 -m json.tool
echo ""

echo -e "${YELLOW}6. Скрытие статьи...${NC}"
curl -s -X PATCH "$BASE_URL/api/v1/articles/$article_id/hide" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"is_hidden": true}' | python3 -m json.tool
echo ""

echo -e "${YELLOW}7. Показ статьи...${NC}"
curl -s -X PATCH "$BASE_URL/api/v1/articles/$article_id/hide" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"is_hidden": false}' | python3 -m json.tool
echo ""

echo -e "${YELLOW}8. Удаление статьи...${NC}"
curl -s -X DELETE "$BASE_URL/api/v1/articles/$article_id" -H "X-API-Key: $API_KEY" | python3 -m json.tool
echo ""

# ============================================================================
# CASES
# ============================================================================
echo -e "\n${BLUE}=== ТЕСТИРОВАНИЕ CASES ===${NC}\n"

echo -e "${YELLOW}1. Создание кейса...${NC}"
case_response=$(curl -s -X POST "$BASE_URL/api/v1/cases/" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Тестовый кейс",
        "about": "Описание тестового кейса",
        "tags": ["Web", "UI", "React"],
        "image": "/images/test-case.jpg"
    }')
echo "$case_response" | python3 -m json.tool
case_id=$(echo "$case_response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
echo -e "${GREEN}Создан кейс ID: $case_id${NC}\n"

echo -e "${YELLOW}2. Получение списка кейсов...${NC}"
curl -s "$BASE_URL/api/v1/cases/" -H "X-API-Key: $API_KEY" | python3 -m json.tool | head -20
echo ""

echo -e "${YELLOW}3. Получение свежих кейсов...${NC}"
curl -s "$BASE_URL/api/v1/cases/fresh" -H "X-API-Key: $API_KEY" | python3 -m json.tool | head -20
echo ""

echo -e "${YELLOW}4. Обновление кейса...${NC}"
curl -s -X PUT "$BASE_URL/api/v1/cases/$case_id" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"name": "Обновленный кейс", "about": "Новое описание"}' | python3 -m json.tool
echo ""

echo -e "${YELLOW}5. Повышение рейтинга до 15...${NC}"
curl -s -X PATCH "$BASE_URL/api/v1/cases/$case_id/rating" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"rating": 15}' | python3 -m json.tool
echo ""

echo -e "${YELLOW}6. Пометка как свежий...${NC}"
curl -s -X PATCH "$BASE_URL/api/v1/cases/$case_id/fresh" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"is_fresh": true}' | python3 -m json.tool
echo ""

echo -e "${YELLOW}7. Скрытие кейса...${NC}"
curl -s -X PATCH "$BASE_URL/api/v1/cases/$case_id/hide" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"is_hidden": true}' | python3 -m json.tool
echo ""

echo -e "${YELLOW}8. Удаление кейса...${NC}"
curl -s -X DELETE "$BASE_URL/api/v1/cases/$case_id" -H "X-API-Key: $API_KEY" | python3 -m json.tool
echo ""

# ============================================================================
# REVIEWS
# ============================================================================
echo -e "\n${BLUE}=== ТЕСТИРОВАНИЕ REVIEWS ===${NC}\n"

echo -e "${YELLOW}1. Создание отзыва...${NC}"
review_response=$(curl -s -X POST "$BASE_URL/api/v1/reviews/" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "Иван Иванов",
        "company": "ООО Тест",
        "review": "Отличная работа, все сделано качественно!",
        "stars": 5,
        "photo": "/images/reviewer.jpg"
    }')
echo "$review_response" | python3 -m json.tool
review_id=$(echo "$review_response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
echo -e "${GREEN}Создан отзыв ID: $review_id${NC}\n"

echo -e "${YELLOW}2. Получение списка отзывов...${NC}"
curl -s "$BASE_URL/api/v1/reviews/" -H "X-API-Key: $API_KEY" | python3 -m json.tool | head -20
echo ""

echo -e "${YELLOW}3. Обновление отзыва...${NC}"
curl -s -X PUT "$BASE_URL/api/v1/reviews/$review_id" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"name": "Петр Петров", "company": "ООО Новая компания"}' | python3 -m json.tool
echo ""

echo -e "${YELLOW}4. Повышение рейтинга до 20...${NC}"
curl -s -X PATCH "$BASE_URL/api/v1/reviews/$review_id/rating" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"rating": 20}' | python3 -m json.tool
echo ""

echo -e "${YELLOW}5. Скрытие отзыва...${NC}"
curl -s -X PATCH "$BASE_URL/api/v1/reviews/$review_id/hide" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"is_hidden": true}' | python3 -m json.tool
echo ""

echo -e "${YELLOW}6. Удаление отзыва...${NC}"
curl -s -X DELETE "$BASE_URL/api/v1/reviews/$review_id" -H "X-API-Key: $API_KEY" | python3 -m json.tool
echo ""

# ============================================================================
# VACANCIES
# ============================================================================
echo -e "\n${BLUE}=== ТЕСТИРОВАНИЕ VACANCIES ===${NC}\n"

echo -e "${YELLOW}1. Создание вакансии...${NC}"
vacancy_response=$(curl -s -X POST "$BASE_URL/api/v1/vacancies/" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
        "title": "Python Developer",
        "url": "https://example.com/vacancy/python-dev",
        "employment_type": "Полная занятость",
        "description": "Требуется опытный Python разработчик"
    }')
echo "$vacancy_response" | python3 -m json.tool
vacancy_id=$(echo "$vacancy_response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
echo -e "${GREEN}Создана вакансия ID: $vacancy_id${NC}\n"

echo -e "${YELLOW}2. Получение списка вакансий...${NC}"
curl -s "$BASE_URL/api/v1/vacancies/" -H "X-API-Key: $API_KEY" | python3 -m json.tool | head -20
echo ""

echo -e "${YELLOW}3. Обновление вакансии...${NC}"
curl -s -X PUT "$BASE_URL/api/v1/vacancies/$vacancy_id" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"title": "Senior Python Developer", "url": "https://example.com/vacancy/senior-python"}' | python3 -m json.tool
echo ""

echo -e "${YELLOW}4. Повышение рейтинга до 25...${NC}"
curl -s -X PATCH "$BASE_URL/api/v1/vacancies/$vacancy_id/rating" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"rating": 25}' | python3 -m json.tool
echo ""

echo -e "${YELLOW}5. Скрытие вакансии...${NC}"
curl -s -X PATCH "$BASE_URL/api/v1/vacancies/$vacancy_id/hide" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d '{"is_hidden": true}' | python3 -m json.tool
echo ""

echo -e "${YELLOW}6. Удаление вакансии...${NC}"
curl -s -X DELETE "$BASE_URL/api/v1/vacancies/$vacancy_id" -H "X-API-Key: $API_KEY" | python3 -m json.tool
echo ""

# ============================================================================
# APPLICATIONS (С ФАЙЛОМ)
# ============================================================================
echo -e "\n${BLUE}=== ТЕСТИРОВАНИЕ APPLICATIONS (С ФАЙЛОМ) ===${NC}\n"

echo "Это тестовое резюме для проверки загрузки файлов" > test_resume.txt

echo -e "${YELLOW}1. Создание заявки с файлом (БЕЗ API ключа)...${NC}"
app_response=$(curl -s -X POST "$BASE_URL/api/v1/applications/" \
    -F "name=Иван Тестовый" \
    -F "email=test@example.com" \
    -F "message=Хочу откликнуться на вакансию" \
    -F "company=ООО Тест" \
    -F "phone=+7 999 123-45-67" \
    -F "file=@test_resume.txt;type=text/plain")
echo "$app_response" | python3 -m json.tool
app_id=$(echo "$app_response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
file_path=$(echo "$app_response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('file_path', 'null'))" 2>/dev/null)
echo -e "${GREEN}Создана заявка ID: $app_id${NC}"
echo -e "${GREEN}Файл сохранен: $file_path${NC}\n"

echo -e "${YELLOW}2. Получение списка заявок (С API ключом)...${NC}"
curl -s "$BASE_URL/api/v1/applications/" -H "X-API-Key: $API_KEY" | python3 -m json.tool | head -30
echo ""

echo -e "${YELLOW}3. Получение заявки по ID...${NC}"
curl -s "$BASE_URL/api/v1/applications/$app_id" -H "X-API-Key: $API_KEY" | python3 -m json.tool
echo ""

echo -e "${YELLOW}4. Изменение статуса на 'in_progress'...${NC}"
curl -s -X PATCH "$BASE_URL/api/v1/applications/$app_id/status?status=in_progress" \
    -H "X-API-Key: $API_KEY" | python3 -m json.tool
echo ""

echo -e "${YELLOW}5. Удаление заявки...${NC}"
curl -s -X DELETE "$BASE_URL/api/v1/applications/$app_id" -H "X-API-Key: $API_KEY" | python3 -m json.tool
echo ""

rm -f test_resume.txt

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}ТЕСТИРОВАНИЕ ЗАВЕРШЕНО${NC}"
echo -e "${GREEN}========================================${NC}\n"
