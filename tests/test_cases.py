"""Тесты для API кейсов."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_case(client: AsyncClient):
    """Тест создания кейса."""
    data = {
        "name": "Новый кейс",
        "about": "Описание кейса",
        "tags": ["Web", "React", "TypeScript"],
        "image_url": "https://example.com/image.png",
        "link_url": "https://example.com/project"
    }
    
    response = await client.post("/api/v1/cases", json=data)
    assert response.status_code == 201
    assert response.json()["name"] == data["name"]
    assert response.json()["tags"] == data["tags"]


@pytest.mark.asyncio
async def test_get_cases(client: AsyncClient):
    """Тест получения всех кейсов."""
    response = await client.get("/api/v1/cases")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_fresh_cases(client: AsyncClient):
    """Тест получения свежих кейсов."""
    # Создаем обычный кейс
    data1 = {
        "name": "Обычный кейс",
        "about": "Описание",
        "tags": ["Web"],
        "image_url": "https://example.com/image.png",
        "link_url": "https://example.com/project"
    }
    await client.post("/api/v1/cases", json=data1)
    
    # Создаем свежий кейс
    data2 = {
        "name": "Свежий кейс",
        "about": "Описание",
        "tags": ["Mobile"],
        "image_url": "https://example.com/image2.png",
        "link_url": "https://example.com/project2"
    }
    create_response = await client.post("/api/v1/cases", json=data2)
    case_id = create_response.json()["id"]
    
    # Помечаем как свежий
    await client.patch(
        f"/api/v1/cases/{case_id}/fresh",
        json={"is_fresh": True}
    )
    
    # Получаем свежие кейсы
    response = await client.get("/api/v1/cases/fresh")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["is_fresh"] is True


@pytest.mark.asyncio
async def test_update_case_rating(client: AsyncClient):
    """Тест обновления рейтинга кейса."""
    # Создаем кейс
    data = {
        "name": "Кейс",
        "about": "Описание",
        "tags": ["Web"],
        "image_url": "https://example.com/image.png",
        "link_url": "https://example.com/project"
    }
    create_response = await client.post("/api/v1/cases", json=data)
    case_id = create_response.json()["id"]
    
    # Обновляем рейтинг
    response = await client.patch(
        f"/api/v1/cases/{case_id}/rating",
        json={"rating": 100}
    )
    assert response.status_code == 200
    assert response.json()["rating"] == 100
