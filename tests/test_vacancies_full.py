"""Полные тесты для API вакансий с валидацией и проверкой ошибок."""
import pytest
from litestar.testing import AsyncTestClient


class TestVacanciesValidation:
    """Тесты валидации данных для вакансий."""
    
    @pytest.mark.asyncio
    async def test_create_vacancy_success(self, client: AsyncTestClient):
        """Тест успешного создания вакансии."""
        data = {
            "title": "Python Developer",
            "url": "https://example.com/job/1",
            "employment_type": "Full-time",
            "description": "Great opportunity"
        }
        
        response = await client.post("/api/v1/vacancies", json=data)
        
        assert response.status_code == 201
        result = response.json()
        assert result["title"] == data["title"]
        assert result["url"] == data["url"]
        assert result["id"] is not None
        assert result["rating"] == 0
        assert result["is_hidden"] is False
    
    @pytest.mark.asyncio
    async def test_create_vacancy_missing_required_fields(self, client: AsyncTestClient):
        """Тест создания вакансии без обязательных полей."""
        # Без title
        response = await client.post("/api/v1/vacancies", json={
            "url": "https://example.com/job",
            "employment_type": "Full-time"
        })
        assert response.status_code == 400
        
        # Без url
        response = await client.post("/api/v1/vacancies", json={
            "title": "Developer",
            "employment_type": "Full-time"
        })
        assert response.status_code == 400
        
        # Без employment_type
        response = await client.post("/api/v1/vacancies", json={
            "title": "Developer",
            "url": "https://example.com/job"
        })
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_create_vacancy_empty_title(self, client: AsyncTestClient):
        """Тест создания вакансии с пустым названием."""
        data = {
            "title": "",
            "url": "https://example.com/job",
            "employment_type": "Full-time"
        }
        
        response = await client.post("/api/v1/vacancies", json=data)
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_create_vacancy_title_too_long(self, client: AsyncTestClient):
        """Тест создания вакансии со слишком длинным названием."""
        data = {
            "title": "A" * 256,  # Максимум 255
            "url": "https://example.com/job",
            "employment_type": "Full-time"
        }
        
        response = await client.post("/api/v1/vacancies", json=data)
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_create_vacancy_invalid_url(self, client: AsyncTestClient):
        """Тест создания вакансии с некорректным URL."""
        data = {
            "title": "Developer",
            "url": "",  # Пустой URL
            "employment_type": "Full-time"
        }
        
        response = await client.post("/api/v1/vacancies", json=data)
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_get_vacancy_not_found(self, client: AsyncTestClient):
        """Тест получения несуществующей вакансии."""
        response = await client.get("/api/v1/vacancies/99999")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_vacancy_not_found(self, client: AsyncTestClient):
        """Тест обновления несуществующей вакансии."""
        data = {"title": "Updated Title"}
        response = await client.put("/api/v1/vacancies/99999", json=data)
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_delete_vacancy_not_found(self, client: AsyncTestClient):
        """Тест удаления несуществующей вакансии."""
        response = await client.delete("/api/v1/vacancies/99999")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_rating_negative(self, client: AsyncTestClient):
        """Тест обновления рейтинга с отрицательным значением."""
        # Сначала создаем вакансию
        data = {
            "title": "Developer",
            "url": "https://example.com/job",
            "employment_type": "Full-time"
        }
        create_response = await client.post("/api/v1/vacancies", json=data)
        vacancy_id = create_response.json()["id"]
        
        # Пытаемся установить отрицательный рейтинг
        response = await client.patch(
            f"/api/v1/vacancies/{vacancy_id}/rating",
            json={"rating": -1}
        )
        assert response.status_code == 400


class TestVacanciesCRUD:
    """Тесты CRUD операций для вакансий."""
    
    @pytest.mark.asyncio
    async def test_full_crud_cycle(self, client: AsyncTestClient):
        """Тест полного цикла CRUD операций."""
        # CREATE
        create_data = {
            "title": "Senior Python Developer",
            "url": "https://example.com/job/senior",
            "employment_type": "Full-time",
            "description": "Senior position"
        }
        create_response = await client.post("/api/v1/vacancies", json=create_data)
        assert create_response.status_code == 201
        vacancy = create_response.json()
        vacancy_id = vacancy["id"]
        
        # READ - Get by ID
        get_response = await client.get(f"/api/v1/vacancies/{vacancy_id}")
        assert get_response.status_code == 200
        assert get_response.json()["title"] == create_data["title"]
        
        # READ - Get all
        list_response = await client.get("/api/v1/vacancies")
        assert list_response.status_code == 200
        assert len(list_response.json()) >= 1
        
        # UPDATE
        update_data = {
            "title": "Lead Python Developer",
            "description": "Updated description"
        }
        update_response = await client.put(
            f"/api/v1/vacancies/{vacancy_id}",
            json=update_data
        )
        assert update_response.status_code == 200
        updated = update_response.json()
        assert updated["title"] == update_data["title"]
        assert updated["description"] == update_data["description"]
        
        # UPDATE RATING
        rating_response = await client.patch(
            f"/api/v1/vacancies/{vacancy_id}/rating",
            json={"rating": 10}
        )
        assert rating_response.status_code == 200
        assert rating_response.json()["rating"] == 10
        
        # HIDE
        hide_response = await client.patch(
            f"/api/v1/vacancies/{vacancy_id}/hide",
            json={"is_hidden": True}
        )
        assert hide_response.status_code == 200
        assert hide_response.json()["is_hidden"] is True
        
        # SHOW
        show_response = await client.patch(
            f"/api/v1/vacancies/{vacancy_id}/hide",
            json={"is_hidden": False}
        )
        assert show_response.status_code == 200
        assert show_response.json()["is_hidden"] is False
        
        # DELETE
        delete_response = await client.delete(f"/api/v1/vacancies/{vacancy_id}")
        assert delete_response.status_code == 200
        
        # Verify deleted
        get_deleted_response = await client.get(f"/api/v1/vacancies/{vacancy_id}")
        assert get_deleted_response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_hidden_vacancies_filter(self, client: AsyncTestClient):
        """Тест фильтрации скрытых вакансий."""
        # Создаем видимую вакансию
        visible_data = {
            "title": "Visible Job",
            "url": "https://example.com/visible",
            "employment_type": "Full-time"
        }
        visible_response = await client.post("/api/v1/vacancies", json=visible_data)
        visible_id = visible_response.json()["id"]
        
        # Создаем скрытую вакансию
        hidden_data = {
            "title": "Hidden Job",
            "url": "https://example.com/hidden",
            "employment_type": "Part-time"
        }
        hidden_response = await client.post("/api/v1/vacancies", json=hidden_data)
        hidden_id = hidden_response.json()["id"]
        
        # Скрываем вторую вакансию
        await client.patch(
            f"/api/v1/vacancies/{hidden_id}/hide",
            json={"is_hidden": True}
        )
        
        # Получаем без скрытых
        response_without_hidden = await client.get("/api/v1/vacancies")
        vacancies_without_hidden = response_without_hidden.json()
        assert all(v["is_hidden"] is False for v in vacancies_without_hidden)
        
        # Получаем со скрытыми
        response_with_hidden = await client.get("/api/v1/vacancies?include_hidden=true")
        vacancies_with_hidden = response_with_hidden.json()
        assert len(vacancies_with_hidden) >= len(vacancies_without_hidden)


class TestVacanciesEdgeCases:
    """Тесты граничных случаев."""
    
    @pytest.mark.asyncio
    async def test_create_vacancy_with_special_characters(self, client: AsyncTestClient):
        """Тест создания вакансии со спецсимволами."""
        data = {
            "title": "Developer <script>alert('xss')</script>",
            "url": "https://example.com/job?param=value&other=123",
            "employment_type": "Full-time",
            "description": "Test with 'quotes' and \"double quotes\""
        }
        
        response = await client.post("/api/v1/vacancies", json=data)
        assert response.status_code == 201
        result = response.json()
        # Проверяем что данные сохранились как есть (без экранирования)
        assert result["title"] == data["title"]
    
    @pytest.mark.asyncio
    async def test_create_vacancy_with_unicode(self, client: AsyncTestClient):
        """Тест создания вакансии с Unicode символами."""
        data = {
            "title": "Разработчик Python 🐍",
            "url": "https://example.com/работа",
            "employment_type": "Полная занятость",
            "description": "Описание на русском языке с эмодзи 😊"
        }
        
        response = await client.post("/api/v1/vacancies", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["title"] == data["title"]
        assert result["description"] == data["description"]
    
    @pytest.mark.asyncio
    async def test_update_vacancy_partial(self, client: AsyncTestClient):
        """Тест частичного обновления вакансии."""
        # Создаем вакансию
        create_data = {
            "title": "Original Title",
            "url": "https://example.com/original",
            "employment_type": "Full-time",
            "description": "Original description"
        }
        create_response = await client.post("/api/v1/vacancies", json=create_data)
        vacancy_id = create_response.json()["id"]
        
        # Обновляем только title
        update_response = await client.put(
            f"/api/v1/vacancies/{vacancy_id}",
            json={"title": "New Title"}
        )
        assert update_response.status_code == 200
        updated = update_response.json()
        assert updated["title"] == "New Title"
        # Остальные поля должны остаться
        assert updated["url"] == create_data["url"]
        assert updated["employment_type"] == create_data["employment_type"]
