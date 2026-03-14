"""Тесты безопасности API - защита от SQL injection и других атак."""
import pytest
from litestar.testing import AsyncTestClient


class TestSQLInjectionProtection:
    """Тесты защиты от SQL injection."""
    
    @pytest.mark.asyncio
    async def test_sql_injection_in_title(self, client: AsyncTestClient):
        """Тест SQL injection в поле title."""
        malicious_data = {
            "title": "'; DROP TABLE vacancies; --",
            "url": "https://example.com/job",
            "employment_type": "Full-time"
        }
        
        # Создаем вакансию с SQL injection попыткой
        response = await client.post("/api/v1/vacancies", json=malicious_data)
        assert response.status_code == 201
        
        # Проверяем что таблица не удалена - можем получить список
        list_response = await client.get("/api/v1/vacancies")
        assert list_response.status_code == 200
        
        # Проверяем что данные сохранились как строка
        vacancy = response.json()
        assert vacancy["title"] == malicious_data["title"]
    
    @pytest.mark.asyncio
    async def test_sql_injection_in_description(self, client: AsyncTestClient):
        """Тест SQL injection в описании."""
        malicious_data = {
            "title": "Developer",
            "url": "https://example.com/job",
            "employment_type": "Full-time",
            "description": "1' OR '1'='1"
        }
        
        response = await client.post("/api/v1/vacancies", json=malicious_data)
        assert response.status_code == 201
        
        # Проверяем что данные сохранились безопасно
        vacancy = response.json()
        assert vacancy["description"] == malicious_data["description"]
    
    @pytest.mark.asyncio
    async def test_sql_injection_in_get_by_id(self, client: AsyncTestClient):
        """Тест SQL injection в параметре ID."""
        # Пытаемся использовать SQL injection в URL параметре
        malicious_ids = [
            "1 OR 1=1",
            "1; DROP TABLE vacancies;",
            "1' UNION SELECT * FROM users--",
        ]
        
        for malicious_id in malicious_ids:
            response = await client.get(f"/api/v1/vacancies/{malicious_id}")
            # Должна быть ошибка валидации или 404, но не 500
            assert response.status_code in [400, 404, 422]
    
    @pytest.mark.asyncio
    async def test_sql_injection_in_review_stars(self, client: AsyncTestClient):
        """Тест SQL injection через поле stars в отзывах."""
        malicious_data = {
            "name": "Test User",
            "company": "Test Company",
            "review": "Great!",
            "stars": "5; DROP TABLE reviews;",
            "photo": "/photo.jpg"
        }
        
        response = await client.post("/api/v1/reviews", json=malicious_data)
        # Должна быть ошибка валидации типа
        assert response.status_code == 400


class TestXSSProtection:
    """Тесты защиты от XSS атак."""
    
    @pytest.mark.asyncio
    async def test_xss_in_title(self, client: AsyncTestClient):
        """Тест XSS в названии."""
        xss_data = {
            "title": "<script>alert('XSS')</script>",
            "url": "https://example.com/job",
            "employment_type": "Full-time"
        }
        
        response = await client.post("/api/v1/vacancies", json=xss_data)
        assert response.status_code == 201
        
        # Данные должны сохраниться как есть (экранирование на фронтенде)
        vacancy = response.json()
        assert vacancy["title"] == xss_data["title"]
    
    @pytest.mark.asyncio
    async def test_xss_in_description(self, client: AsyncTestClient):
        """Тест XSS в описании."""
        xss_data = {
            "title": "Developer",
            "url": "https://example.com/job",
            "employment_type": "Full-time",
            "description": "<img src=x onerror=alert('XSS')>"
        }
        
        response = await client.post("/api/v1/vacancies", json=xss_data)
        assert response.status_code == 201
        
        vacancy = response.json()
        assert vacancy["description"] == xss_data["description"]


class TestInputValidation:
    """Тесты валидации входных данных."""
    
    @pytest.mark.asyncio
    async def test_extremely_long_input(self, client: AsyncTestClient):
        """Тест с очень длинными данными."""
        long_data = {
            "title": "A" * 10000,  # Очень длинное название
            "url": "https://example.com/job",
            "employment_type": "Full-time"
        }
        
        response = await client.post("/api/v1/vacancies", json=long_data)
        # Должна быть ошибка валидации
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_null_bytes_in_input(self, client: AsyncTestClient):
        """Тест с null bytes."""
        data = {
            "title": "Developer\x00Admin",
            "url": "https://example.com/job",
            "employment_type": "Full-time"
        }
        
        response = await client.post("/api/v1/vacancies", json=data)
        # API должен обработать или отклонить
        assert response.status_code in [201, 400]
    
    @pytest.mark.asyncio
    async def test_invalid_json(self, client: AsyncTestClient):
        """Тест с невалидным JSON."""
        response = await client.post(
            "/api/v1/vacancies",
            content=b"{'invalid': json}",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_wrong_data_types(self, client: AsyncTestClient):
        """Тест с неправильными типами данных."""
        # Строка вместо числа для rating
        data = {
            "title": "Developer",
            "url": "https://example.com/job",
            "employment_type": "Full-time"
        }
        create_response = await client.post("/api/v1/vacancies", json=data)
        vacancy_id = create_response.json()["id"]
        
        # Пытаемся установить строку как рейтинг
        response = await client.patch(
            f"/api/v1/vacancies/{vacancy_id}/rating",
            json={"rating": "not_a_number"}
        )
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_negative_id(self, client: AsyncTestClient):
        """Тест с отрицательным ID."""
        response = await client.get("/api/v1/vacancies/-1")
        assert response.status_code in [400, 404, 422]
    
    @pytest.mark.asyncio
    async def test_zero_id(self, client: AsyncTestClient):
        """Тест с нулевым ID."""
        response = await client.get("/api/v1/vacancies/0")
        assert response.status_code in [400, 404, 422]


class TestMassAssignment:
    """Тесты защиты от mass assignment."""
    
    @pytest.mark.asyncio
    async def test_cannot_set_id_on_create(self, client: AsyncTestClient):
        """Тест что нельзя установить ID при создании."""
        data = {
            "id": 999,  # Пытаемся установить свой ID
            "title": "Developer",
            "url": "https://example.com/job",
            "employment_type": "Full-time"
        }
        
        response = await client.post("/api/v1/vacancies", json=data)
        # ID должен быть проигнорирован или вызвать ошибку
        if response.status_code == 201:
            vacancy = response.json()
            # ID должен быть назначен автоматически, не 999
            assert vacancy["id"] != 999
    
    @pytest.mark.asyncio
    async def test_cannot_modify_created_at(self, client: AsyncTestClient):
        """Тест что нельзя изменить created_at."""
        # Создаем вакансию
        create_data = {
            "title": "Developer",
            "url": "https://example.com/job",
            "employment_type": "Full-time"
        }
        create_response = await client.post("/api/v1/vacancies", json=create_data)
        vacancy = create_response.json()
        original_created_at = vacancy["created_at"]
        
        # Пытаемся изменить created_at
        update_data = {
            "title": "Updated",
            "created_at": "2020-01-01T00:00:00Z"
        }
        update_response = await client.put(
            f"/api/v1/vacancies/{vacancy['id']}",
            json=update_data
        )
        
        if update_response.status_code == 200:
            updated = update_response.json()
            # created_at не должен измениться
            assert updated["created_at"] == original_created_at


class TestRateLimiting:
    """Тесты на устойчивость к большому количеству запросов."""
    
    @pytest.mark.asyncio
    async def test_multiple_rapid_requests(self, client: AsyncTestClient):
        """Тест множественных быстрых запросов."""
        # Отправляем 50 запросов подряд
        for i in range(50):
            data = {
                "title": f"Job {i}",
                "url": f"https://example.com/job/{i}",
                "employment_type": "Full-time"
            }
            response = await client.post("/api/v1/vacancies", json=data)
            # Все запросы должны обрабатываться
            assert response.status_code in [201, 429]  # 429 если есть rate limiting


class TestAuthorizationBypass:
    """Тесты попыток обхода авторизации."""
    
    @pytest.mark.asyncio
    async def test_access_without_auth_headers(self, client: AsyncTestClient):
        """Тест доступа без заголовков авторизации."""
        # В текущей реализации нет авторизации, но API должен работать
        response = await client.get("/api/v1/vacancies")
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_malicious_headers(self, client: AsyncTestClient):
        """Тест с вредоносными заголовками."""
        headers = {
            "X-Forwarded-For": "'; DROP TABLE vacancies; --",
            "User-Agent": "<script>alert('XSS')</script>",
            "Referer": "javascript:alert('XSS')"
        }
        
        response = await client.get("/api/v1/vacancies", headers=headers)
        # API должен обработать запрос нормально
        assert response.status_code == 200
