#!/usr/bin/env python3
"""
Скрипт для тестирования всех endpoints API.
Использование: python scripts/test_api.py
"""
import requests
import json
from typing import Optional

# Конфигурация
BASE_URL = "http://localhost:8000"
API_KEY = "internal-bot-key-2026"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
HEADERS_NO_KEY = {"Content-Type": "application/json"}


def print_response(response: requests.Response, title: str):
    """Красиво выводит ответ."""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")


def test_vacancies():
    """Тестирование вакансий."""
    print("\n\n🔵 ТЕСТИРОВАНИЕ ВАКАНСИЙ")
    
    # 1. Создание вакансии
    vacancy_data = {
        "title": "Python Developer",
        "description": "Разработка backend на Python",
        "requirements": "Python, FastAPI, PostgreSQL",
        "salary": "150000-200000",
        "location": "Москва",
        "employment_type": "full_time"
    }
    r = requests.post(f"{BASE_URL}/api/v1/vacancies", json=vacancy_data, headers=HEADERS)
    print_response(r, "POST /api/v1/vacancies - Создание вакансии")
    vacancy_id = r.json().get("id") if r.status_code == 201 else None
    
    # 2. Получение всех вакансий
    r = requests.get(f"{BASE_URL}/api/v1/vacancies", headers=HEADERS)
    print_response(r, "GET /api/v1/vacancies - Список вакансий")
    
    if vacancy_id:
        # 3. Получение одной вакансии
        r = requests.get(f"{BASE_URL}/api/v1/vacancies/{vacancy_id}", headers=HEADERS)
        print_response(r, f"GET /api/v1/vacancies/{vacancy_id} - Одна вакансия")
        
        # 4. Обновление рейтинга
        r = requests.patch(
            f"{BASE_URL}/api/v1/vacancies/{vacancy_id}/rating",
            json={"rating": 5},
            headers=HEADERS
        )
        print_response(r, f"PATCH /api/v1/vacancies/{vacancy_id}/rating - Обновление рейтинга")
        
        # 5. Скрытие вакансии
        r = requests.patch(
            f"{BASE_URL}/api/v1/vacancies/{vacancy_id}/hide",
            json={"is_hidden": True},
            headers=HEADERS
        )
        print_response(r, f"PATCH /api/v1/vacancies/{vacancy_id}/hide - Скрытие вакансии")
        
        # 6. Удаление вакансии
        r = requests.delete(f"{BASE_URL}/api/v1/vacancies/{vacancy_id}", headers=HEADERS)
        print_response(r, f"DELETE /api/v1/vacancies/{vacancy_id} - Удаление вакансии")


def test_reviews():
    """Тестирование отзывов."""
    print("\n\n🔵 ТЕСТИРОВАНИЕ ОТЗЫВОВ")
    
    # 1. Создание отзыва
    review_data = {
        "author_name": "Иван Петров",
        "author_position": "CEO",
        "company_name": "Tech Corp",
        "content": "Отличная работа, рекомендую!",
        "rating": 5
    }
    r = requests.post(f"{BASE_URL}/api/v1/reviews", json=review_data, headers=HEADERS)
    print_response(r, "POST /api/v1/reviews - Создание отзыва")
    review_id = r.json().get("id") if r.status_code == 201 else None
    
    # 2. Получение всех отзывов
    r = requests.get(f"{BASE_URL}/api/v1/reviews", headers=HEADERS)
    print_response(r, "GET /api/v1/reviews - Список отзывов")
    
    if review_id:
        # 3. Получение одного отзыва
        r = requests.get(f"{BASE_URL}/api/v1/reviews/{review_id}", headers=HEADERS)
        print_response(r, f"GET /api/v1/reviews/{review_id} - Один отзыв")
        
        # 4. Удаление отзыва
        r = requests.delete(f"{BASE_URL}/api/v1/reviews/{review_id}", headers=HEADERS)
        print_response(r, f"DELETE /api/v1/reviews/{review_id} - Удаление отзыва")


def test_articles():
    """Тестирование статей."""
    print("\n\n🔵 ТЕСТИРОВАНИЕ СТАТЕЙ")
    
    # 1. Создание статьи
    article_data = {
        "title": "Как мы разработали новый продукт",
        "content": "Подробная история разработки...",
        "author": "Команда разработки",
        "preview": "Краткое описание статьи"
    }
    r = requests.post(f"{BASE_URL}/api/v1/articles", json=article_data, headers=HEADERS)
    print_response(r, "POST /api/v1/articles - Создание статьи")
    article_id = r.json().get("id") if r.status_code == 201 else None
    
    # 2. Получение всех статей
    r = requests.get(f"{BASE_URL}/api/v1/articles", headers=HEADERS)
    print_response(r, "GET /api/v1/articles - Список статей")
    
    if article_id:
        # 3. Получение одной статьи
        r = requests.get(f"{BASE_URL}/api/v1/articles/{article_id}", headers=HEADERS)
        print_response(r, f"GET /api/v1/articles/{article_id} - Одна статья")
        
        # 4. Удаление статьи
        r = requests.delete(f"{BASE_URL}/api/v1/articles/{article_id}", headers=HEADERS)
        print_response(r, f"DELETE /api/v1/articles/{article_id} - Удаление статьи")


def test_cases():
    """Тестирование кейсов."""
    print("\n\n🔵 ТЕСТИРОВАНИЕ КЕЙСОВ")
    
    # 1. Создание кейса
    case_data = {
        "title": "Разработка интернет-магазина",
        "description": "Полный цикл разработки e-commerce платформы",
        "client": "Retail Company",
        "technologies": ["Python", "React", "PostgreSQL"],
        "result": "Увеличение продаж на 150%"
    }
    r = requests.post(f"{BASE_URL}/api/v1/cases", json=case_data, headers=HEADERS)
    print_response(r, "POST /api/v1/cases - Создание кейса")
    case_id = r.json().get("id") if r.status_code == 201 else None
    
    # 2. Получение всех кейсов
    r = requests.get(f"{BASE_URL}/api/v1/cases", headers=HEADERS)
    print_response(r, "GET /api/v1/cases - Список кейсов")
    
    if case_id:
        # 3. Получение одного кейса
        r = requests.get(f"{BASE_URL}/api/v1/cases/{case_id}", headers=HEADERS)
        print_response(r, f"GET /api/v1/cases/{case_id} - Один кейс")
        
        # 4. Пометка как свежий
        r = requests.patch(
            f"{BASE_URL}/api/v1/cases/{case_id}/fresh",
            json={"is_fresh": True},
            headers=HEADERS
        )
        print_response(r, f"PATCH /api/v1/cases/{case_id}/fresh - Пометка как свежий")
        
        # 5. Удаление кейса
        r = requests.delete(f"{BASE_URL}/api/v1/cases/{case_id}", headers=HEADERS)
        print_response(r, f"DELETE /api/v1/cases/{case_id} - Удаление кейса")


def test_applications():
    """Тестирование заявок."""
    print("\n\n🔵 ТЕСТИРОВАНИЕ ЗАЯВОК")
    
    # 1. Создание заявки БЕЗ API ключа (публичный endpoint)
    app_data = {
        "name": "Алексей Смирнов",
        "email": "alexey@example.com",
        "phone": "+79991234567",
        "message": "Хочу заказать разработку сайта"
    }
    r = requests.post(f"{BASE_URL}/api/v1/applications", json=app_data, headers=HEADERS_NO_KEY)
    print_response(r, "POST /api/v1/applications - Создание заявки (БЕЗ API ключа)")
    app_id = r.json().get("id") if r.status_code == 201 else None
    
    # 2. Получение всех заявок (С API ключом)
    r = requests.get(f"{BASE_URL}/api/v1/applications", headers=HEADERS)
    print_response(r, "GET /api/v1/applications - Список заявок (С API ключом)")
    
    if app_id:
        # 3. Получение одной заявки
        r = requests.get(f"{BASE_URL}/api/v1/applications/{app_id}", headers=HEADERS)
        print_response(r, f"GET /api/v1/applications/{app_id} - Одна заявка")
        
        # 4. Обновление статуса
        r = requests.patch(
            f"{BASE_URL}/api/v1/applications/{app_id}/status",
            json={"status": "in_progress"},
            headers=HEADERS
        )
        print_response(r, f"PATCH /api/v1/applications/{app_id}/status - Обновление статуса")
        
        # 5. Удаление заявки
        r = requests.delete(f"{BASE_URL}/api/v1/applications/{app_id}", headers=HEADERS)
        print_response(r, f"DELETE /api/v1/applications/{app_id} - Удаление заявки")


def test_auth():
    """Тестирование аутентификации."""
    print("\n\n🔵 ТЕСТИРОВАНИЕ АУТЕНТИФИКАЦИИ")
    
    # 1. Запрос БЕЗ API ключа (должен вернуть 401)
    r = requests.get(f"{BASE_URL}/api/v1/vacancies")
    print_response(r, "GET /api/v1/vacancies - БЕЗ API ключа (ожидается 401)")
    
    # 2. Запрос с неверным API ключом (должен вернуть 401)
    bad_headers = {"X-API-Key": "wrong-key"}
    r = requests.get(f"{BASE_URL}/api/v1/vacancies", headers=bad_headers)
    print_response(r, "GET /api/v1/vacancies - С неверным ключом (ожидается 401)")
    
    # 3. Запрос с правильным API ключом (должен вернуть 200)
    r = requests.get(f"{BASE_URL}/api/v1/vacancies", headers=HEADERS)
    print_response(r, "GET /api/v1/vacancies - С правильным ключом (ожидается 200)")


def main():
    """Запуск всех тестов."""
    print("🚀 ЗАПУСК ТЕСТИРОВАНИЯ API")
    print(f"Base URL: {BASE_URL}")
    print(f"API Key: {API_KEY}")
    
    try:
        # Проверка доступности API
        r = requests.get(f"{BASE_URL}/health")
        if r.status_code != 200:
            print("❌ API недоступен! Запустите сервер: python main.py")
            return
        print("✅ API доступен")
        
        # Запуск тестов
        test_auth()
        test_vacancies()
        test_reviews()
        test_articles()
        test_cases()
        test_applications()
        
        print("\n\n" + "="*60)
        print("✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ОШИБКА: Не удается подключиться к API")
        print("Убедитесь что сервер запущен: python main.py")
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")


if __name__ == "__main__":
    main()
