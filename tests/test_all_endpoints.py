"""Полное тестирование всех API endpoints."""
import pytest
from litestar.testing import AsyncTestClient


class TestHealthEndpoints:
    """Тесты health endpoints."""
    
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncTestClient):
        """Тест health check."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "backend-api"
        assert data["version"] == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncTestClient):
        """Тест корневого endpoint."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data
        assert "health" in data


class TestVacanciesEndpoints:
    """Тесты всех endpoints вакансий."""
    
    @pytest.mark.asyncio
    async def test_create_vacancy(self, client: AsyncTestClient):
        """POST /api/v1/vacancies - Создание вакансии."""
        data = {
            "title": "Python Developer",
            "url": "https://example.com/job/1",
            "employment_type": "Full-time",
            "description": "Great job"
        }
        response = await client.post("/api/v1/vacancies", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["title"] == data["title"]
        assert result["id"] is not None
    
    @pytest.mark.asyncio
    async def test_get_all_vacancies(self, client: AsyncTestClient):
        """GET /api/v1/vacancies - Получение всех вакансий."""
        response = await client.get("/api/v1/vacancies")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    @pytest.mark.asyncio
    async def test_get_vacancy_by_id(self, client: AsyncTestClient):
        """GET /api/v1/vacancies/{id} - Получение вакансии по ID."""
        # Создаем вакансию
        create_data = {
            "title": "Test Job",
            "url": "https://example.com/test",
            "employment_type": "Full-time"
        }
        create_response = await client.post("/api/v1/vacancies", json=create_data)
        vacancy_id = create_response.json()["id"]
        
        # Получаем по ID
        response = await client.get(f"/api/v1/vacancies/{vacancy_id}")
        assert response.status_code == 200
        assert response.json()["id"] == vacancy_id
    
    @pytest.mark.asyncio
    async def test_update_vacancy(self, client: AsyncTestClient):
        """PUT /api/v1/vacancies/{id} - Обновление вакансии."""
        # Создаем
        create_data = {
            "title": "Original",
            "url": "https://example.com/original",
            "employment_type": "Full-time"
        }
        create_response = await client.post("/api/v1/vacancies", json=create_data)
        vacancy_id = create_response.json()["id"]
        
        # Обновляем
        update_data = {"title": "Updated"}
        response = await client.put(f"/api/v1/vacancies/{vacancy_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["title"] == "Updated"
    
    @pytest.mark.asyncio
    async def test_update_vacancy_rating(self, client: AsyncTestClient):
        """PATCH /api/v1/vacancies/{id}/rating - Обновление рейтинга."""
        create_data = {
            "title": "Job",
            "url": "https://example.com/job",
            "employment_type": "Full-time"
        }
        create_response = await client.post("/api/v1/vacancies", json=create_data)
        vacancy_id = create_response.json()["id"]
        
        response = await client.patch(
            f"/api/v1/vacancies/{vacancy_id}/rating",
            json={"rating": 10}
        )
        assert response.status_code == 200
        assert response.json()["rating"] == 10
    
    @pytest.mark.asyncio
    async def test_hide_vacancy(self, client: AsyncTestClient):
        """PATCH /api/v1/vacancies/{id}/hide - Скрытие вакансии."""
        create_data = {
            "title": "Job",
            "url": "https://example.com/job",
            "employment_type": "Full-time"
        }
        create_response = await client.post("/api/v1/vacancies", json=create_data)
        vacancy_id = create_response.json()["id"]
        
        response = await client.patch(
            f"/api/v1/vacancies/{vacancy_id}/hide",
            json={"is_hidden": True}
        )
        assert response.status_code == 200
        assert response.json()["is_hidden"] is True
    
    @pytest.mark.asyncio
    async def test_delete_vacancy(self, client: AsyncTestClient):
        """DELETE /api/v1/vacancies/{id} - Удаление вакансии."""
        create_data = {
            "title": "Job",
            "url": "https://example.com/job",
            "employment_type": "Full-time"
        }
        create_response = await client.post("/api/v1/vacancies", json=create_data)
        vacancy_id = create_response.json()["id"]
        
        response = await client.delete(f"/api/v1/vacancies/{vacancy_id}")
        assert response.status_code == 200
        
        # Проверяем что удалено
        get_response = await client.get(f"/api/v1/vacancies/{vacancy_id}")
        assert get_response.status_code == 404


class TestReviewsEndpoints:
    """Тесты всех endpoints отзывов."""
    
    @pytest.mark.asyncio
    async def test_create_review(self, client: AsyncTestClient):
        """POST /api/v1/reviews - Создание отзыва."""
        data = {
            "name": "John Doe",
            "company": "Tech Corp",
            "review": "Great company!",
            "stars": 5,
            "photo": "/photo.jpg"
        }
        response = await client.post("/api/v1/reviews", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["name"] == data["name"]
        assert result["stars"] == data["stars"]
    
    @pytest.mark.asyncio
    async def test_get_all_reviews(self, client: AsyncTestClient):
        """GET /api/v1/reviews - Получение всех отзывов."""
        response = await client.get("/api/v1/reviews")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    @pytest.mark.asyncio
    async def test_get_review_by_id(self, client: AsyncTestClient):
        """GET /api/v1/reviews/{id} - Получение отзыва по ID."""
        create_data = {
            "name": "Test User",
            "company": "Test Co",
            "review": "Good",
            "stars": 4
        }
        create_response = await client.post("/api/v1/reviews", json=create_data)
        review_id = create_response.json()["id"]
        
        response = await client.get(f"/api/v1/reviews/{review_id}")
        assert response.status_code == 200
        assert response.json()["id"] == review_id
    
    @pytest.mark.asyncio
    async def test_update_review(self, client: AsyncTestClient):
        """PUT /api/v1/reviews/{id} - Обновление отзыва."""
        create_data = {
            "name": "User",
            "company": "Company",
            "review": "Original",
            "stars": 3
        }
        create_response = await client.post("/api/v1/reviews", json=create_data)
        review_id = create_response.json()["id"]
        
        update_data = {"review": "Updated review"}
        response = await client.put(f"/api/v1/reviews/{review_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["review"] == "Updated review"
    
    @pytest.mark.asyncio
    async def test_update_review_rating(self, client: AsyncTestClient):
        """PATCH /api/v1/reviews/{id}/rating - Обновление рейтинга."""
        create_data = {
            "name": "User",
            "company": "Company",
            "review": "Good",
            "stars": 5
        }
        create_response = await client.post("/api/v1/reviews", json=create_data)
        review_id = create_response.json()["id"]
        
        response = await client.patch(
            f"/api/v1/reviews/{review_id}/rating",
            json={"rating": 15}
        )
        assert response.status_code == 200
        assert response.json()["rating"] == 15
    
    @pytest.mark.asyncio
    async def test_hide_review(self, client: AsyncTestClient):
        """PATCH /api/v1/reviews/{id}/hide - Скрытие отзыва."""
        create_data = {
            "name": "User",
            "company": "Company",
            "review": "Good",
            "stars": 5
        }
        create_response = await client.post("/api/v1/reviews", json=create_data)
        review_id = create_response.json()["id"]
        
        response = await client.patch(
            f"/api/v1/reviews/{review_id}/hide",
            json={"is_hidden": True}
        )
        assert response.status_code == 200
        assert response.json()["is_hidden"] is True
    
    @pytest.mark.asyncio
    async def test_delete_review(self, client: AsyncTestClient):
        """DELETE /api/v1/reviews/{id} - Удаление отзыва."""
        create_data = {
            "name": "User",
            "company": "Company",
            "review": "Good",
            "stars": 5
        }
        create_response = await client.post("/api/v1/reviews", json=create_data)
        review_id = create_response.json()["id"]
        
        response = await client.delete(f"/api/v1/reviews/{review_id}")
        assert response.status_code == 200


class TestArticlesEndpoints:
    """Тесты всех endpoints статей."""
    
    @pytest.mark.asyncio
    async def test_create_article(self, client: AsyncTestClient):
        """POST /api/v1/articles - Создание статьи."""
        data = {
            "title": "How to code",
            "url": "https://blog.example.com/article",
            "photo": "/images/article.jpg"
        }
        response = await client.post("/api/v1/articles", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["title"] == data["title"]
    
    @pytest.mark.asyncio
    async def test_get_all_articles(self, client: AsyncTestClient):
        """GET /api/v1/articles - Получение всех статей."""
        response = await client.get("/api/v1/articles")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    @pytest.mark.asyncio
    async def test_get_article_by_id(self, client: AsyncTestClient):
        """GET /api/v1/articles/{id} - Получение статьи по ID."""
        create_data = {
            "title": "Article",
            "url": "https://example.com/article"
        }
        create_response = await client.post("/api/v1/articles", json=create_data)
        article_id = create_response.json()["id"]
        
        response = await client.get(f"/api/v1/articles/{article_id}")
        assert response.status_code == 200
        assert response.json()["id"] == article_id
    
    @pytest.mark.asyncio
    async def test_update_article(self, client: AsyncTestClient):
        """PUT /api/v1/articles/{id} - Обновление статьи."""
        create_data = {
            "title": "Original",
            "url": "https://example.com/original"
        }
        create_response = await client.post("/api/v1/articles", json=create_data)
        article_id = create_response.json()["id"]
        
        update_data = {"title": "Updated Article"}
        response = await client.put(f"/api/v1/articles/{article_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Article"
    
    @pytest.mark.asyncio
    async def test_update_article_rating(self, client: AsyncTestClient):
        """PATCH /api/v1/articles/{id}/rating - Обновление рейтинга."""
        create_data = {
            "title": "Article",
            "url": "https://example.com/article"
        }
        create_response = await client.post("/api/v1/articles", json=create_data)
        article_id = create_response.json()["id"]
        
        response = await client.patch(
            f"/api/v1/articles/{article_id}/rating",
            json={"rating": 20}
        )
        assert response.status_code == 200
        assert response.json()["rating"] == 20
    
    @pytest.mark.asyncio
    async def test_hide_article(self, client: AsyncTestClient):
        """PATCH /api/v1/articles/{id}/hide - Скрытие статьи."""
        create_data = {
            "title": "Article",
            "url": "https://example.com/article"
        }
        create_response = await client.post("/api/v1/articles", json=create_data)
        article_id = create_response.json()["id"]
        
        response = await client.patch(
            f"/api/v1/articles/{article_id}/hide",
            json={"is_hidden": True}
        )
        assert response.status_code == 200
        assert response.json()["is_hidden"] is True
    
    @pytest.mark.asyncio
    async def test_delete_article(self, client: AsyncTestClient):
        """DELETE /api/v1/articles/{id} - Удаление статьи."""
        create_data = {
            "title": "Article",
            "url": "https://example.com/article"
        }
        create_response = await client.post("/api/v1/articles", json=create_data)
        article_id = create_response.json()["id"]
        
        response = await client.delete(f"/api/v1/articles/{article_id}")
        assert response.status_code == 200


class TestCasesEndpoints:
    """Тесты всех endpoints кейсов."""
    
    @pytest.mark.asyncio
    async def test_create_case(self, client: AsyncTestClient):
        """POST /api/v1/cases - Создание кейса."""
        data = {
            "name": "Bank Project",
            "about": "Online banking system",
            "tags": ["Web", "Python", "React"],
            "image": "/images/case.png"
        }
        response = await client.post("/api/v1/cases", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["name"] == data["name"]
        assert result["tags"] == data["tags"]
    
    @pytest.mark.asyncio
    async def test_get_all_cases(self, client: AsyncTestClient):
        """GET /api/v1/cases - Получение всех кейсов."""
        response = await client.get("/api/v1/cases")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    @pytest.mark.asyncio
    async def test_get_fresh_cases(self, client: AsyncTestClient):
        """GET /api/v1/cases/fresh - Получение свежих кейсов."""
        response = await client.get("/api/v1/cases/fresh")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    @pytest.mark.asyncio
    async def test_get_case_by_id(self, client: AsyncTestClient):
        """GET /api/v1/cases/{id} - Получение кейса по ID."""
        create_data = {
            "name": "Project",
            "about": "Description",
            "tags": ["Web"],
            "image": "/image.png"
        }
        create_response = await client.post("/api/v1/cases", json=create_data)
        case_id = create_response.json()["id"]
        
        response = await client.get(f"/api/v1/cases/{case_id}")
        assert response.status_code == 200
        assert response.json()["id"] == case_id
    
    @pytest.mark.asyncio
    async def test_update_case(self, client: AsyncTestClient):
        """PUT /api/v1/cases/{id} - Обновление кейса."""
        create_data = {
            "name": "Original",
            "about": "Original description",
            "tags": ["Web"],
            "image": "/image.png"
        }
        create_response = await client.post("/api/v1/cases", json=create_data)
        case_id = create_response.json()["id"]
        
        update_data = {"name": "Updated Case"}
        response = await client.put(f"/api/v1/cases/{case_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Case"
    
    @pytest.mark.asyncio
    async def test_update_case_rating(self, client: AsyncTestClient):
        """PATCH /api/v1/cases/{id}/rating - Обновление рейтинга."""
        create_data = {
            "name": "Case",
            "about": "Description",
            "tags": ["Web"],
            "image": "/image.png"
        }
        create_response = await client.post("/api/v1/cases", json=create_data)
        case_id = create_response.json()["id"]
        
        response = await client.patch(
            f"/api/v1/cases/{case_id}/rating",
            json={"rating": 25}
        )
        assert response.status_code == 200
        assert response.json()["rating"] == 25
    
    @pytest.mark.asyncio
    async def test_toggle_case_fresh(self, client: AsyncTestClient):
        """PATCH /api/v1/cases/{id}/fresh - Пометка как свежий."""
        create_data = {
            "name": "Case",
            "about": "Description",
            "tags": ["Web"],
            "image": "/image.png"
        }
        create_response = await client.post("/api/v1/cases", json=create_data)
        case_id = create_response.json()["id"]
        
        response = await client.patch(
            f"/api/v1/cases/{case_id}/fresh",
            json={"is_fresh": True}
        )
        assert response.status_code == 200
        assert response.json()["is_fresh"] is True
    
    @pytest.mark.asyncio
    async def test_hide_case(self, client: AsyncTestClient):
        """PATCH /api/v1/cases/{id}/hide - Скрытие кейса."""
        create_data = {
            "name": "Case",
            "about": "Description",
            "tags": ["Web"],
            "image": "/image.png"
        }
        create_response = await client.post("/api/v1/cases", json=create_data)
        case_id = create_response.json()["id"]
        
        response = await client.patch(
            f"/api/v1/cases/{case_id}/hide",
            json={"is_hidden": True}
        )
        assert response.status_code == 200
        assert response.json()["is_hidden"] is True
    
    @pytest.mark.asyncio
    async def test_delete_case(self, client: AsyncTestClient):
        """DELETE /api/v1/cases/{id} - Удаление кейса."""
        create_data = {
            "name": "Case",
            "about": "Description",
            "tags": ["Web"],
            "image": "/image.png"
        }
        create_response = await client.post("/api/v1/cases", json=create_data)
        case_id = create_response.json()["id"]
        
        response = await client.delete(f"/api/v1/cases/{case_id}")
        assert response.status_code == 200
