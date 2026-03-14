#!/usr/bin/env python3
"""
Полное тестирование всех API эндпоинтов.
Тестирует каждый раздел: создание → обновление → рейтинг → удаление
"""
import requests
import json
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"
API_KEY = "internal-bot-key-2026"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# Цвета для вывода
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def print_section(title):
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{title:^80}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

def print_test(name, success, response=None):
    status = f"{GREEN}✓ PASS{RESET}" if success else f"{RED}✗ FAIL{RESET}"
    print(f"{status} | {name}")
    if response and not success:
        print(f"  {RED}Ответ: {response.text[:200]}{RESET}")

def test_articles():
    """Тестирование раздела Articles"""
    print_section("ТЕСТИРОВАНИЕ ARTICLES")
    article_id = None
    
    # 1. Создание статьи
    data = {
        "title": "Тестовая статья",
        "content": "Это содержание тестовой статьи для проверки API",
        "author": "Тестовый автор"
    }
    r = requests.post(f"{BASE_URL}/api/v1/articles/", json=data, headers=HEADERS)
    success = r.status_code == 201
    print_test("POST /api/v1/articles/ - Создание статьи", success, r)
    if success:
        article_id = r.json()["id"]
        print(f"  {YELLOW}Создана статья ID: {article_id}{RESET}")
    
    # 2. Получение списка статей
    r = requests.get(f"{BASE_URL}/api/v1/articles/", headers=HEADERS)
    success = r.status_code == 200 and len(r.json()) > 0
    print_test("GET /api/v1/articles/ - Список статей", success, r)
    
    if article_id:
        # 3. Получение конкретной статьи
        r = requests.get(f"{BASE_URL}/api/v1/articles/{article_id}", headers=HEADERS)
        success = r.status_code == 200
        print_test(f"GET /api/v1/articles/{article_id} - Получение статьи", success, r)
        
        # 4. Обновление статьи
        update_data = {
            "title": "Обновленная статья",
            "content": "Обновленное содержание"
        }
        r = requests.put(f"{BASE_URL}/api/v1/articles/{article_id}", json=update_data, headers=HEADERS)
        success = r.status_code == 200
        print_test(f"PUT /api/v1/articles/{article_id} - Обновление статьи", success, r)
        
        # 5. Обновление рейтинга
        rating_data = {"rating": 10}
        r = requests.patch(f"{BASE_URL}/api/v1/articles/{article_id}/rating", json=rating_data, headers=HEADERS)
        success = r.status_code == 200
        print_test(f"PATCH /api/v1/articles/{article_id}/rating - Повышение рейтинга", success, r)
        
        # 6. Скрытие статьи
        hide_data = {"is_hidden": True}
        r = requests.patch(f"{BASE_URL}/api/v1/articles/{article_id}/hide", json=hide_data, headers=HEADERS)
        success = r.status_code == 200
        print_test(f"PATCH /api/v1/articles/{article_id}/hide - Скрытие статьи", success, r)
        
        # 7. Показ статьи
        show_data = {"is_hidden": False}
        r = requests.patch(f"{BASE_URL}/api/v1/articles/{article_id}/hide", json=show_data, headers=HEADERS)
        success = r.status_code == 200
        print_test(f"PATCH /api/v1/articles/{article_id}/hide - Показ статьи", success, r)
        
        # 8. Удаление статьи
        r = requests.delete(f"{BASE_URL}/api/v1/articles/{article_id}", headers=HEADERS)
        success = r.status_code == 200
        print_test(f"DELETE /api/v1/articles/{article_id} - Удаление статьи", success, r)

def test_cases():
    """Тестирование раздела Cases"""
    print_section("ТЕСТИРОВАНИЕ CASES")
    case_id = None
    
    # 1. Создание кейса
    data = {
        "title": "Тестовый кейс",
        "description": "Описание тестового кейса для проверки API",
        "client": "Тестовый клиент",
        "technologies": "Python, FastAPI, PostgreSQL"
    }
    r = requests.post(f"{BASE_URL}/api/v1/cases/", json=data, headers=HEADERS)
    success = r.status_code == 201
    print_test("POST /api/v1/cases/ - Создание кейса", success, r)
    if success:
        case_id = r.json()["id"]
        print(f"  {YELLOW}Создан кейс ID: {case_id}{RESET}")
    
    # 2. Получение списка кейсов
    r = requests.get(f"{BASE_URL}/api/v1/cases/", headers=HEADERS)
    success = r.status_code == 200
    print_test("GET /api/v1/cases/ - Список кейсов", success, r)
    
    # 3. Получение свежих кейсов
    r = requests.get(f"{BASE_URL}/api/v1/cases/fresh", headers=HEADERS)
    success = r.status_code == 200
    print_test("GET /api/v1/cases/fresh - Свежие кейсы", success, r)
    
    if case_id:
        # 4. Получение конкретного кейса
        r = requests.get(f"{BASE_URL}/api/v1/cases/{case_id}", headers=HEADERS)
        success = r.status_code == 200
        print_test(f"GET /api/v1/cases/{case_id} - Получение кейса", success, r)
        
        # 5. Обновление кейса
        update_data = {
            "title": "Обновленный кейс",
            "description": "Обновленное описание кейса"
        }
        r = requests.put(f"{BASE_URL}/api/v1/cases/{case_id}", json=update_data, headers=HEADERS)
        success = r.status_code == 200
        print_test(f"PUT /api/v1/cases/{case_id} - Обновление кейса", success, r)
        
        # 6. Обновление рейтинга
        rating_data = {"rating": 15}
        r = requests.patch(f"{BASE_URL}/api/v1/cases/{case_id}/rating", json=rating_data, headers=HEADERS)
        success = r.status_code == 200
        print_test(f"PATCH /api/v1/cases/{case_id}/rating - Повышение рейтинга", success, r)
        
        # 7. Пометка как свежий
        fresh_data = {"is_fresh": True}
        r = requests.patch(f"{BASE_URL}/api/v1/cases/{case_id}/fresh", json=fresh_data, headers=HEADERS)
        success = r.status_code == 200
        print_test(f"PATCH /api/v1/cases/{case_id}/fresh - Пометка свежим", success, r)
        
        # 8. Скрытие кейса
        hide_data = {"is_hidden": True}
        r = requests.patch(f"{BASE_URL}/api/v1/cases/{case_id}/hide", json=hide_data, headers=HEADERS)
        success = r.status_code == 200
        print_test(f"PATCH /api/v1/cases/{case_id}/hide - Скрытие кейса", success, r)
        
        # 9. Удаление кейса
        r = requests.delete(f"{BASE_URL}/api/v1/cases/{case_id}", headers=HEADERS)
        success = r.status_code == 200
        print_test(f"DELETE /api/v1/cases/{case_id} - Удаление кейса", success, r)

def test_reviews():
    """Тестирование раздела Reviews"""
    print_section("ТЕСТИРОВАНИЕ REVIEWS")
    review_id = None
    
    # 1. Создание отзыва
    data = {
        "author": "Тестовый автор отзыва",
        "content": "Это тестовый отзыв для проверки API",
        "rating": 5
    }
    r = requests.post(f"{BASE_URL}/api/v1/reviews/", json=data, headers=HEADERS)
    success = r.status_code == 201
    print_test("POST /api/v1/reviews/ - Создание отзыва", success, r)
    if success:
        review_id = r.json()["id"]
        print(f"  {YELLOW}Создан отзыв ID: {review_id}{RESET}")
    
    # 2. Получение списка отзывов
    r = requests.get(f"{BASE_URL}/api/v1/reviews/", headers=HEADERS)
    success = r.status_code == 200
    print_test("GET /api/v1/reviews/ - Список отзывов", success, r)
    
    if review_id:
        # 3. Получение конкретного отзыва
        r = requests.get(f"{BASE_URL}/api/v1/reviews/{review_id}", headers=HEADERS)
        success = r.status_code == 200
        print_test(f"GET /api/v1/reviews/{review_id} - Получение отзыва", success, r)
        
        # 4. Обновление отзыва
        update_data = {
            "author": "Обновленный автор",
            "content": "Обновленный отзыв"
        }
        r = requests.put(f"{BASE_URL}/api/v1/reviews/{review_id}", json=update_data, headers=HEADERS)
        success = r.status_code == 200
        print_test(f"PUT /api/v1/reviews/{review_id} - Обновление отзыва", success, r)
        
        # 5. Обновление рейтинга
        rating_data = {"rating": 20}
        r = requests.patch(f"{BASE_URL}/api/v1/reviews/{review_id}/rating", json=rating_data, headers=HEADERS)
        success = r.status_code == 200
        print_test(f"PATCH /api/v1/reviews/{review_id}/rating - Повышение рейтинга", success, r)
        
        # 6. Скрытие отзыва
        hide_data = {"is_hidden": True}
        r = requests.patch(f"{BASE_URL}/api/v1/reviews/{review_id}/hide", json=hide_data, headers=HEADERS)
        success = r.status_code == 200
        print_test(f"PATCH /api/v1/reviews/{review_id}/hide - Скрытие отзыва", success, r)
        
        # 7. Удаление отзыва
        r = requests.delete(f"{BASE_URL}/api/v1/reviews/{review_id}", headers=HEADERS)
        success = r.status_code == 200
        print_test(f"DELETE /api/v1/reviews/{review_id} - Удаление отзыва", success, r)

def test_vacancies():
    """Тестирование раздела Vacancies"""
    print_section("ТЕСТИРОВАНИЕ VACANCIES")
    vacancy_id = None
    
    # 1. Создание вакансии
    data = {
        "title": "Тестовая вакансия Python Developer",
        "description": "Описание тестовой вакансии для проверки API",
        "requirements": "Python, FastAPI, PostgreSQL",
        "salary_from": 100000,
        "salary_to": 200000,
        "location": "Москва",
        "employment_type": "Полная занятость",
        "experience": "3-5 лет"
    }
    r = requests.post(f"{BASE_URL}/api/v1/vacancies/", json=data, headers=HEADERS)
    success = r.status_code == 201
    print_test("POST /api/v1/vacancies/ - Создание вакансии", success, r)
    if success:
        vacancy_id = r.json()["id"]
        print(f"  {YELLOW}Создана вакансия ID: {vacancy_id}{RESET}")
    
    # 2. Получение списка вакансий
    r = requests.get(f"{BASE_URL}/api/v1/vacancies/", headers=HEADERS)
    success = r.status_code == 200
    print_test("GET /api/v1/vacancies/ - Список вакансий", success, r)
    
    if vacancy_id:
        # 3. Получение конкретной вакансии
        r = requests.get(f"{BASE_URL}/api/v1/vacancies/{vacancy_id}", headers=HEADERS)
        success = r.status_code == 200
        print_test(f"GET /api/v1/vacancies/{vacancy_id} - Получение вакансии", success, r)
        
        # 4. Обновление вакансии
        update_data = {
            "title": "Обновленная вакансия Senior Python Developer",
            "salary_from": 150000,
            "salary_to": 250000
        }
        r = requests.put(f"{BASE_URL}/api/v1/vacancies/{vacancy_id}", json=update_data, headers=HEADERS)
        success = r.status_code == 200
        print_test(f"PUT /api/v1/vacancies/{vacancy_id} - Обновление вакансии", success, r)
        
        # 5. Обновление рейтинга
        rating_data = {"rating": 25}
        r = requests.patch(f"{BASE_URL}/api/v1/vacancies/{vacancy_id}/rating", json=rating_data, headers=HEADERS)
        success = r.status_code == 200
        print_test(f"PATCH /api/v1/vacancies/{vacancy_id}/rating - Повышение рейтинга", success, r)
        
        # 6. Скрытие вакансии
        hide_data = {"is_hidden": True}
        r = requests.patch(f"{BASE_URL}/api/v1/vacancies/{vacancy_id}/hide", json=hide_data, headers=HEADERS)
        success = r.status_code == 200
        print_test(f"PATCH /api/v1/vacancies/{vacancy_id}/hide - Скрытие вакансии", success, r)
        
        # 7. Удаление вакансии
        r = requests.delete(f"{BASE_URL}/api/v1/vacancies/{vacancy_id}", headers=HEADERS)
        success = r.status_code == 200
        print_test(f"DELETE /api/v1/vacancies/{vacancy_id} - Удаление вакансии", success, r)

def test_applications():
    """Тестирование раздела Applications (с файлом)"""
    print_section("ТЕСТИРОВАНИЕ APPLICATIONS (С ФАЙЛОМ)")
    application_id = None
    
    # 1. Создание тестового файла
    test_file_path = Path("test_resume.txt")
    test_file_path.write_text("Это тестовое резюме для проверки загрузки файлов через API")
    
    # 2. Создание заявки с файлом (БЕЗ API ключа!)
    files = {"file": ("test_resume.txt", open(test_file_path, "rb"), "text/plain")}
    data = {
        "name": "Иван Тестовый",
        "email": "test@example.com",
        "message": "Хочу откликнуться на вакансию",
        "company": "ООО Тест",
        "phone": "+7 999 123-45-67"
    }
    # Важно: для applications НЕ используем API ключ!
    r = requests.post(f"{BASE_URL}/api/v1/applications/", data=data, files=files)
    success = r.status_code == 201
    print_test("POST /api/v1/applications/ - Создание заявки с файлом (БЕЗ API ключа)", success, r)
    if success:
        application_id = r.json()["id"]
        file_path = r.json().get("file_path")
        print(f"  {YELLOW}Создана заявка ID: {application_id}{RESET}")
        print(f"  {YELLOW}Файл сохранен: {file_path}{RESET}")
    
    # 3. Получение списка заявок (С API ключом)
    r = requests.get(f"{BASE_URL}/api/v1/applications/", headers=HEADERS)
    success = r.status_code == 200
    print_test("GET /api/v1/applications/ - Список заявок", success, r)
    
    if application_id:
        # 4. Получение конкретной заявки
        r = requests.get(f"{BASE_URL}/api/v1/applications/{application_id}", headers=HEADERS)
        success = r.status_code == 200
        print_test(f"GET /api/v1/applications/{application_id} - Получение заявки", success, r)
        
        # 5. Изменение статуса заявки
        r = requests.patch(f"{BASE_URL}/api/v1/applications/{application_id}/status?status=in_progress", headers=HEADERS)
        success = r.status_code == 200
        print_test(f"PATCH /api/v1/applications/{application_id}/status - Изменение статуса", success, r)
        
        # 6. Удаление заявки
        r = requests.delete(f"{BASE_URL}/api/v1/applications/{application_id}", headers=HEADERS)
        success = r.status_code == 200
        print_test(f"DELETE /api/v1/applications/{application_id} - Удаление заявки", success, r)
    
    # Удаляем тестовый файл
    test_file_path.unlink(missing_ok=True)

def test_health():
    """Тестирование health endpoint"""
    print_section("ТЕСТИРОВАНИЕ HEALTH")
    r = requests.get(f"{BASE_URL}/health")
    success = r.status_code == 200
    print_test("GET /health - Проверка здоровья API", success, r)
    if success:
        print(f"  {YELLOW}Статус: {r.json()}{RESET}")

if __name__ == "__main__":
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}ПОЛНОЕ ТЕСТИРОВАНИЕ API{RESET}")
    print(f"{BLUE}Base URL: {BASE_URL}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}")
    
    try:
        test_health()
        test_articles()
        test_cases()
        test_reviews()
        test_vacancies()
        test_applications()
        
        print(f"\n{GREEN}{'='*80}{RESET}")
        print(f"{GREEN}ТЕСТИРОВАНИЕ ЗАВЕРШЕНО{RESET}")
        print(f"{GREEN}{'='*80}{RESET}\n")
    except Exception as e:
        print(f"\n{RED}ОШИБКА: {e}{RESET}\n")
        sys.exit(1)
