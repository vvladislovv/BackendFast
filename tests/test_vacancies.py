"""Тесты для API вакансий."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_vacancy(client: AsyncClient):
    """Тест создания вакансии."""
    data = {
        "title": "Python Developer",
        "url": "https://example.com/job",
        "employment_type": "Full-time",
        "description": "Great opportunity"
    }
    
    response = await client.post("/api/v1/vacancies", json=data)
    assert response.status_code == 201
    assert response.json()["title"] == data["title"]


@pytest.mark.asyncio
async def test_get_vacancies(client: AsyncClient):
    """Тест получения всех вакансий."""
    response = await client.get("/api/v1/vacancies")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_vacancy_by_id(client: AsyncClient):
    """Тест получения вакансии по ID."""
    # Создаем вакансию
    data = {
        "title": "Python Developer",
        "url": "https://example.com/job",
        "employment_type": "Full-time"
    }
    create_response = await client.post("/api/v1/vacancies", json=data)
    vacancy_id = create_response.json()["id"]
    
    # Получаем вакансию
    response = await client.get(f"/api/v1/vacancies/{vacancy_id}")
    assert response.status_code == 200
    assert response.json()["id"] == vacancy_id
