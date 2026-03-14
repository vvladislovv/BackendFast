#!/bin/bash

# API ключ для доступа
API_KEY="internal-bot-key-2026"

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
NC='\033[0m'

PASSED=0
FAILED=0
TOTAL=0

test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local expected=$4
    local description=$5
    
    TOTAL=$((TOTAL + 1))
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -H "X-API-Key: $API_KEY" "http://localhost:8000$endpoint")
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "http://localhost:8000$endpoint" \
            -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" -d "$data")
    elif [ "$method" = "PUT" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PUT "http://localhost:8000$endpoint" \
            -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" -d "$data")
    elif [ "$method" = "PATCH" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PATCH "http://localhost:8000$endpoint" \
            -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" -d "$data")
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -w "\n%{http_code}" -X DELETE -H "X-API-Key: $API_KEY" "http://localhost:8000$endpoint")
    fi
    
    status=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status" = "$expected" ]; then
        echo -e "${GREEN}✓${NC} $method $endpoint - $description"
        PASSED=$((PASSED + 1))
        echo "$body"
    else
        echo -e "${RED}✗${NC} $method $endpoint - Expected $expected, got $status"
        FAILED=$((FAILED + 1))
    fi
}

echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}ТЕСТИРОВАНИЕ ВСЕХ API ENDPOINTS${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Health
echo -e "${YELLOW}=== Health Endpoints ===${NC}"
test_endpoint "GET" "/health" "" "200" "Health check"
test_endpoint "GET" "/" "" "200" "Root endpoint"

# Vacancies
echo -e "\n${YELLOW}=== Vacancies Endpoints ===${NC}"
VACANCY_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/vacancies \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{"title":"Test Job","url":"https://example.com/test","employment_type":"Full-time"}')
VACANCY_ID=$(echo "$VACANCY_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "1")

test_endpoint "POST" "/api/v1/vacancies" '{"title":"Python Dev","url":"https://example.com/job","employment_type":"Full-time"}' "201" "Create vacancy"
test_endpoint "GET" "/api/v1/vacancies" "" "200" "Get all vacancies"
test_endpoint "GET" "/api/v1/vacancies/$VACANCY_ID" "" "200" "Get vacancy by ID"
test_endpoint "PUT" "/api/v1/vacancies/$VACANCY_ID" '{"title":"Updated"}' "200" "Update vacancy"
test_endpoint "PATCH" "/api/v1/vacancies/$VACANCY_ID/rating" '{"rating":10}' "200" "Update rating"
test_endpoint "PATCH" "/api/v1/vacancies/$VACANCY_ID/hide" '{"is_hidden":true}' "200" "Hide vacancy"
test_endpoint "DELETE" "/api/v1/vacancies/$VACANCY_ID" "" "200" "Delete vacancy"

# Reviews
echo -e "\n${YELLOW}=== Reviews Endpoints ===${NC}"
REVIEW_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/reviews \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{"name":"John","company":"Tech","review":"Good","stars":5}')
REVIEW_ID=$(echo "$REVIEW_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "1")

test_endpoint "POST" "/api/v1/reviews" '{"name":"Test","company":"Co","review":"Great","stars":5}' "201" "Create review"
test_endpoint "GET" "/api/v1/reviews" "" "200" "Get all reviews"
test_endpoint "GET" "/api/v1/reviews/$REVIEW_ID" "" "200" "Get review by ID"
test_endpoint "PUT" "/api/v1/reviews/$REVIEW_ID" '{"review":"Updated"}' "200" "Update review"
test_endpoint "PATCH" "/api/v1/reviews/$REVIEW_ID/rating" '{"rating":15}' "200" "Update rating"
test_endpoint "PATCH" "/api/v1/reviews/$REVIEW_ID/hide" '{"is_hidden":true}' "200" "Hide review"
test_endpoint "DELETE" "/api/v1/reviews/$REVIEW_ID" "" "200" "Delete review"

# Articles
echo -e "\n${YELLOW}=== Articles Endpoints ===${NC}"
ARTICLE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/articles \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{"title":"Article","url":"https://example.com/article"}')
ARTICLE_ID=$(echo "$ARTICLE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "1")

test_endpoint "POST" "/api/v1/articles" '{"title":"Test Article","url":"https://example.com/test"}' "201" "Create article"
test_endpoint "GET" "/api/v1/articles" "" "200" "Get all articles"
test_endpoint "GET" "/api/v1/articles/$ARTICLE_ID" "" "200" "Get article by ID"
test_endpoint "PUT" "/api/v1/articles/$ARTICLE_ID" '{"title":"Updated"}' "200" "Update article"
test_endpoint "PATCH" "/api/v1/articles/$ARTICLE_ID/rating" '{"rating":20}' "200" "Update rating"
test_endpoint "PATCH" "/api/v1/articles/$ARTICLE_ID/hide" '{"is_hidden":true}' "200" "Hide article"
test_endpoint "DELETE" "/api/v1/articles/$ARTICLE_ID" "" "200" "Delete article"

# Cases
echo -e "\n${YELLOW}=== Cases Endpoints ===${NC}"
CASE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/cases \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{"name":"Project","about":"Description","tags":["Web"],"image":"/img.png"}')
CASE_ID=$(echo "$CASE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "1")

test_endpoint "POST" "/api/v1/cases" '{"name":"Test Case","about":"Test","tags":["Web"],"image":"/test.png"}' "201" "Create case"
test_endpoint "GET" "/api/v1/cases" "" "200" "Get all cases"
test_endpoint "GET" "/api/v1/cases/fresh" "" "200" "Get fresh cases"
test_endpoint "GET" "/api/v1/cases/$CASE_ID" "" "200" "Get case by ID"
test_endpoint "PUT" "/api/v1/cases/$CASE_ID" '{"name":"Updated"}' "200" "Update case"
test_endpoint "PATCH" "/api/v1/cases/$CASE_ID/rating" '{"rating":25}' "200" "Update rating"
test_endpoint "PATCH" "/api/v1/cases/$CASE_ID/fresh" '{"is_fresh":true}' "200" "Mark as fresh"
test_endpoint "PATCH" "/api/v1/cases/$CASE_ID/hide" '{"is_hidden":true}' "200" "Hide case"
test_endpoint "DELETE" "/api/v1/cases/$CASE_ID" "" "200" "Delete case"

# Результаты
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Всего тестов: $TOTAL"
echo -e "${GREEN}Успешно: $PASSED${NC}"
echo -e "${RED}Провалено: $FAILED${NC}"
PERCENT=$((PASSED * 100 / TOTAL))
echo -e "Процент успеха: $PERCENT%"
echo -e "${BLUE}========================================${NC}\n"
