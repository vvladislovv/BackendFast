#!/bin/bash

# Полное тестирование всех API эндпоинтов
# Тестирует каждый раздел: создание → обновление → рейтинг → удаление

BASE_URL="http://localhost:8000"
API_KEY="internal-bot-key-2026"

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_section() {
    echo -e "\n${BLUE}================================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================================================${NC}\n"
}

print_test() {
    local name=$1
    local status_code=$2
    local expected=$3
    local body=$4
    
    if [ "$status_code" -eq "$expected" ]; then
        echo -e "${GREEN}✓ PASS${NC} | $name (HTTP $status_code)"
    else
        echo -e "${RED}✗ FAIL${NC} | $name (HTTP $status_code, ожидалось $expected)"
        if [ -n "$body" ]; then
            echo -e "  ${RED}Ответ: ${body:0:300}${NC}"
        fi
    fi
}

# ============================================================================
# HEALTH CHECK
# ============================================================================
test_health() {
    print_section "ТЕСТИРОВАНИЕ HEALTH"
    
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL/health")
    status_code=$(echo "$response" | tail -1)
    body=$(echo "$response" | sed '$d')
    
    print_test "GET /health - Проверка здоровья API" "$status_code" 200 "$body"
    echo -e "  ${YELLOW}Ответ: $body${NC}"
}

# ============================================================================
# ARTICLES
# ============================================================================
test_articles() {
    print_section "ТЕСТИРОВАНИЕ ARTICLES"
    
    # 1. Создание статьи
    echo -e "${YELLOW}1. Создание статьи...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/articles/" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{
            "title": "Тестовая статья",
            "content": "Это содержание тестовой статьи для проверки API",
            "author": "Тестовый автор"
        }')
    status_code=$(echo "$response" | tail -1)
    body=$(echo "$response" | sed '$d')
    print_test "POST /api/v1/articles/ - Создание статьи" "$status_code" 201 "$body"
    
    article_id=$(echo "$body" | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')
    echo -e "  ${YELLOW}Создана статья ID: $article_id${NC}"
    
    # 2. Получение списка статей
    echo -e "\n${YELLOW}2. Получение списка статей...${NC}"
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/v1/articles/" \
        -H "X-API-Key: $API_KEY")
    status_code=$(echo "$response" | tail -n1)
    print_test "GET /api/v1/articles/ - Список статей" "$status_code" 200
    
    # 3. Получение конкретной статьи
    echo -e "\n${YELLOW}3. Получение статьи по ID...${NC}"
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/v1/articles/$article_id" \
        -H "X-API-Key: $API_KEY")
    status_code=$(echo "$response" | tail -n1)
    print_test "GET /api/v1/articles/$article_id - Получение статьи" "$status_code" 200
    
    # 4. Обновление статьи
    echo -e "\n${YELLOW}4. Обновление статьи...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X PUT "$BASE_URL/api/v1/articles/$article_id" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{
            "title": "Обновленная статья",
            "content": "Обновленное содержание"
        }')
    status_code=$(echo "$response" | tail -n1)
    print_test "PUT /api/v1/articles/$article_id - Обновление статьи" "$status_code" 200
    
    # 5. Обновление рейтинга
    echo -e "\n${YELLOW}5. Повышение рейтинга...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X PATCH "$BASE_URL/api/v1/articles/$article_id/rating" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"rating": 10}')
    status_code=$(echo "$response" | tail -n1)
    print_test "PATCH /api/v1/articles/$article_id/rating - Повышение рейтинга" "$status_code" 200
    
    # 6. Скрытие статьи
    echo -e "\n${YELLOW}6. Скрытие статьи...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X PATCH "$BASE_URL/api/v1/articles/$article_id/hide" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"is_hidden": true}')
    status_code=$(echo "$response" | tail -n1)
    print_test "PATCH /api/v1/articles/$article_id/hide - Скрытие статьи" "$status_code" 200
    
    # 7. Показ статьи
    echo -e "\n${YELLOW}7. Показ статьи...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X PATCH "$BASE_URL/api/v1/articles/$article_id/hide" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"is_hidden": false}')
    status_code=$(echo "$response" | tail -n1)
    print_test "PATCH /api/v1/articles/$article_id/hide - Показ статьи" "$status_code" 200
    
    # 8. Удаление статьи
    echo -e "\n${YELLOW}8. Удаление статьи...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL/api/v1/articles/$article_id" \
        -H "X-API-Key: $API_KEY")
    status_code=$(echo "$response" | tail -n1)
    print_test "DELETE /api/v1/articles/$article_id - Удаление статьи" "$status_code" 200
}

# ============================================================================
# CASES
# ============================================================================
test_cases() {
    print_section "ТЕСТИРОВАНИЕ CASES"
    
    # 1. Создание кейса
    echo -e "${YELLOW}1. Создание кейса...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/cases/" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{
            "title": "Тестовый кейс",
            "description": "Описание тестового кейса для проверки API",
            "client": "Тестовый клиент",
            "technologies": "Python, FastAPI, PostgreSQL"
        }')
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    print_test "POST /api/v1/cases/ - Создание кейса" "$status_code" 201
    
    case_id=$(echo "$body" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
    echo -e "  ${YELLOW}Создан кейс ID: $case_id${NC}"
    
    # 2. Получение списка кейсов
    echo -e "\n${YELLOW}2. Получение списка кейсов...${NC}"
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/v1/cases/" \
        -H "X-API-Key: $API_KEY")
    status_code=$(echo "$response" | tail -n1)
    print_test "GET /api/v1/cases/ - Список кейсов" "$status_code" 200
    
    # 3. Получение свежих кейсов
    echo -e "\n${YELLOW}3. Получение свежих кейсов...${NC}"
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/v1/cases/fresh" \
        -H "X-API-Key: $API_KEY")
    status_code=$(echo "$response" | tail -n1)
    print_test "GET /api/v1/cases/fresh - Свежие кейсы" "$status_code" 200
    
    # 4. Получение конкретного кейса
    echo -e "\n${YELLOW}4. Получение кейса по ID...${NC}"
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/v1/cases/$case_id" \
        -H "X-API-Key: $API_KEY")
    status_code=$(echo "$response" | tail -n1)
    print_test "GET /api/v1/cases/$case_id - Получение кейса" "$status_code" 200
    
    # 5. Обновление кейса
    echo -e "\n${YELLOW}5. Обновление кейса...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X PUT "$BASE_URL/api/v1/cases/$case_id" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{
            "title": "Обновленный кейс",
            "description": "Обновленное описание кейса"
        }')
    status_code=$(echo "$response" | tail -n1)
    print_test "PUT /api/v1/cases/$case_id - Обновление кейса" "$status_code" 200
    
    # 6. Обновление рейтинга
    echo -e "\n${YELLOW}6. Повышение рейтинга...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X PATCH "$BASE_URL/api/v1/cases/$case_id/rating" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"rating": 15}')
    status_code=$(echo "$response" | tail -n1)
    print_test "PATCH /api/v1/cases/$case_id/rating - Повышение рейтинга" "$status_code" 200
    
    # 7. Пометка как свежий
    echo -e "\n${YELLOW}7. Пометка как свежий...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X PATCH "$BASE_URL/api/v1/cases/$case_id/fresh" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"is_fresh": true}')
    status_code=$(echo "$response" | tail -n1)
    print_test "PATCH /api/v1/cases/$case_id/fresh - Пометка свежим" "$status_code" 200
    
    # 8. Скрытие кейса
    echo -e "\n${YELLOW}8. Скрытие кейса...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X PATCH "$BASE_URL/api/v1/cases/$case_id/hide" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"is_hidden": true}')
    status_code=$(echo "$response" | tail -n1)
    print_test "PATCH /api/v1/cases/$case_id/hide - Скрытие кейса" "$status_code" 200
    
    # 9. Удаление кейса
    echo -e "\n${YELLOW}9. Удаление кейса...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL/api/v1/cases/$case_id" \
        -H "X-API-Key: $API_KEY")
    status_code=$(echo "$response" | tail -n1)
    print_test "DELETE /api/v1/cases/$case_id - Удаление кейса" "$status_code" 200
}

# ============================================================================
# REVIEWS
# ============================================================================
test_reviews() {
    print_section "ТЕСТИРОВАНИЕ REVIEWS"
    
    # 1. Создание отзыва
    echo -e "${YELLOW}1. Создание отзыва...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/reviews/" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{
            "author": "Тестовый автор отзыва",
            "content": "Это тестовый отзыв для проверки API",
            "rating": 5
        }')
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    print_test "POST /api/v1/reviews/ - Создание отзыва" "$status_code" 201
    
    review_id=$(echo "$body" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
    echo -e "  ${YELLOW}Создан отзыв ID: $review_id${NC}"
    
    # 2. Получение списка отзывов
    echo -e "\n${YELLOW}2. Получение списка отзывов...${NC}"
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/v1/reviews/" \
        -H "X-API-Key: $API_KEY")
    status_code=$(echo "$response" | tail -n1)
    print_test "GET /api/v1/reviews/ - Список отзывов" "$status_code" 200
    
    # 3. Получение конкретного отзыва
    echo -e "\n${YELLOW}3. Получение отзыва по ID...${NC}"
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/v1/reviews/$review_id" \
        -H "X-API-Key: $API_KEY")
    status_code=$(echo "$response" | tail -n1)
    print_test "GET /api/v1/reviews/$review_id - Получение отзыва" "$status_code" 200
    
    # 4. Обновление отзыва
    echo -e "\n${YELLOW}4. Обновление отзыва...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X PUT "$BASE_URL/api/v1/reviews/$review_id" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{
            "author": "Обновленный автор",
            "content": "Обновленный отзыв"
        }')
    status_code=$(echo "$response" | tail -n1)
    print_test "PUT /api/v1/reviews/$review_id - Обновление отзыва" "$status_code" 200
    
    # 5. Обновление рейтинга
    echo -e "\n${YELLOW}5. Повышение рейтинга...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X PATCH "$BASE_URL/api/v1/reviews/$review_id/rating" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"rating": 20}')
    status_code=$(echo "$response" | tail -n1)
    print_test "PATCH /api/v1/reviews/$review_id/rating - Повышение рейтинга" "$status_code" 200
    
    # 6. Скрытие отзыва
    echo -e "\n${YELLOW}6. Скрытие отзыва...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X PATCH "$BASE_URL/api/v1/reviews/$review_id/hide" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"is_hidden": true}')
    status_code=$(echo "$response" | tail -n1)
    print_test "PATCH /api/v1/reviews/$review_id/hide - Скрытие отзыва" "$status_code" 200
    
    # 7. Удаление отзыва
    echo -e "\n${YELLOW}7. Удаление отзыва...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL/api/v1/reviews/$review_id" \
        -H "X-API-Key: $API_KEY")
    status_code=$(echo "$response" | tail -n1)
    print_test "DELETE /api/v1/reviews/$review_id - Удаление отзыва" "$status_code" 200
}

# ============================================================================
# VACANCIES
# ============================================================================
test_vacancies() {
    print_section "ТЕСТИРОВАНИЕ VACANCIES"
    
    # 1. Создание вакансии
    echo -e "${YELLOW}1. Создание вакансии...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/vacancies/" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{
            "title": "Тестовая вакансия Python Developer",
            "description": "Описание тестовой вакансии для проверки API",
            "requirements": "Python, FastAPI, PostgreSQL",
            "salary_from": 100000,
            "salary_to": 200000,
            "location": "Москва",
            "employment_type": "Полная занятость",
            "experience": "3-5 лет"
        }')
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    print_test "POST /api/v1/vacancies/ - Создание вакансии" "$status_code" 201
    
    vacancy_id=$(echo "$body" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
    echo -e "  ${YELLOW}Создана вакансия ID: $vacancy_id${NC}"
    
    # 2. Получение списка вакансий
    echo -e "\n${YELLOW}2. Получение списка вакансий...${NC}"
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/v1/vacancies/" \
        -H "X-API-Key: $API_KEY")
    status_code=$(echo "$response" | tail -n1)
    print_test "GET /api/v1/vacancies/ - Список вакансий" "$status_code" 200
    
    # 3. Получение конкретной вакансии
    echo -e "\n${YELLOW}3. Получение вакансии по ID...${NC}"
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/v1/vacancies/$vacancy_id" \
        -H "X-API-Key: $API_KEY")
    status_code=$(echo "$response" | tail -n1)
    print_test "GET /api/v1/vacancies/$vacancy_id - Получение вакансии" "$status_code" 200
    
    # 4. Обновление вакансии
    echo -e "\n${YELLOW}4. Обновление вакансии...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X PUT "$BASE_URL/api/v1/vacancies/$vacancy_id" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{
            "title": "Обновленная вакансия Senior Python Developer",
            "salary_from": 150000,
            "salary_to": 250000
        }')
    status_code=$(echo "$response" | tail -n1)
    print_test "PUT /api/v1/vacancies/$vacancy_id - Обновление вакансии" "$status_code" 200
    
    # 5. Обновление рейтинга
    echo -e "\n${YELLOW}5. Повышение рейтинга...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X PATCH "$BASE_URL/api/v1/vacancies/$vacancy_id/rating" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"rating": 25}')
    status_code=$(echo "$response" | tail -n1)
    print_test "PATCH /api/v1/vacancies/$vacancy_id/rating - Повышение рейтинга" "$status_code" 200
    
    # 6. Скрытие вакансии
    echo -e "\n${YELLOW}6. Скрытие вакансии...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X PATCH "$BASE_URL/api/v1/vacancies/$vacancy_id/hide" \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"is_hidden": true}')
    status_code=$(echo "$response" | tail -n1)
    print_test "PATCH /api/v1/vacancies/$vacancy_id/hide - Скрытие вакансии" "$status_code" 200
    
    # 7. Удаление вакансии
    echo -e "\n${YELLOW}7. Удаление вакансии...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL/api/v1/vacancies/$vacancy_id" \
        -H "X-API-Key: $API_KEY")
    status_code=$(echo "$response" | tail -n1)
    print_test "DELETE /api/v1/vacancies/$vacancy_id - Удаление вакансии" "$status_code" 200
}

# ============================================================================
# APPLICATIONS (С ФАЙЛОМ)
# ============================================================================
test_applications() {
    print_section "ТЕСТИРОВАНИЕ APPLICATIONS (С ФАЙЛОМ)"
    
    # 1. Создание тестового файла
    echo "Это тестовое резюме для проверки загрузки файлов через API" > test_resume.txt
    
    # 2. Создание заявки с файлом (БЕЗ API ключа!)
    echo -e "${YELLOW}1. Создание заявки с файлом (БЕЗ API ключа)...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/applications/" \
        -F "name=Иван Тестовый" \
        -F "email=test@example.com" \
        -F "message=Хочу откликнуться на вакансию" \
        -F "company=ООО Тест" \
        -F "phone=+7 999 123-45-67" \
        -F "file=@test_resume.txt")
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    print_test "POST /api/v1/applications/ - Создание заявки с файлом" "$status_code" 201
    
    application_id=$(echo "$body" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
    echo -e "  ${YELLOW}Создана заявка ID: $application_id${NC}"
    
    # 3. Получение списка заявок (С API ключом)
    echo -e "\n${YELLOW}2. Получение списка заявок...${NC}"
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/v1/applications/" \
        -H "X-API-Key: $API_KEY")
    status_code=$(echo "$response" | tail -n1)
    print_test "GET /api/v1/applications/ - Список заявок" "$status_code" 200
    
    # 4. Получение конкретной заявки
    echo -e "\n${YELLOW}3. Получение заявки по ID...${NC}"
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/v1/applications/$application_id" \
        -H "X-API-Key: $API_KEY")
    status_code=$(echo "$response" | tail -n1)
    print_test "GET /api/v1/applications/$application_id - Получение заявки" "$status_code" 200
    
    # 5. Изменение статуса заявки
    echo -e "\n${YELLOW}4. Изменение статуса заявки...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X PATCH "$BASE_URL/api/v1/applications/$application_id/status?status=in_progress" \
        -H "X-API-Key: $API_KEY")
    status_code=$(echo "$response" | tail -n1)
    print_test "PATCH /api/v1/applications/$application_id/status - Изменение статуса" "$status_code" 200
    
    # 6. Удаление заявки
    echo -e "\n${YELLOW}5. Удаление заявки...${NC}"
    response=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL/api/v1/applications/$application_id" \
        -H "X-API-Key: $API_KEY")
    status_code=$(echo "$response" | tail -n1)
    print_test "DELETE /api/v1/applications/$application_id - Удаление заявки" "$status_code" 200
    
    # Удаляем тестовый файл
    rm -f test_resume.txt
}

# ============================================================================
# MAIN
# ============================================================================
main() {
    echo -e "${BLUE}================================================================================${NC}"
    echo -e "${BLUE}                        ПОЛНОЕ ТЕСТИРОВАНИЕ API${NC}"
    echo -e "${BLUE}                        Base URL: $BASE_URL${NC}"
    echo -e "${BLUE}================================================================================${NC}"
    
    test_health
    test_articles
    test_cases
    test_reviews
    test_vacancies
    test_applications
    
    echo -e "\n${GREEN}================================================================================${NC}"
    echo -e "${GREEN}                        ТЕСТИРОВАНИЕ ЗАВЕРШЕНО${NC}"
    echo -e "${GREEN}================================================================================${NC}\n"
}

main
