"""Тесты для API отзывов."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_review(client: AsyncClient):
    """Тест создания отзыва."""
    data = {
        "name": "Иван Иванов",
        "company": "Tech Corp",
        "review_text": "Отличная работа!",
        "stars": 5,
        "photo_url": "https://example.com/photo.jpg"
    }
    
    response = await client.post("/api/v1/reviews", json=data)
    assert response.status_code == 201
    assert response.json()["name"] == data["name"]
    assert response.json()["stars"] == data["stars"]


@pytest.mark.asyncio
async def test_get_reviews(client: AsyncClient):
    """Тест получения всех отзывов."""
    response = await client.get("/api/v1/reviews")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_update_review(client: AsyncClient):
    """Тест обновления отзыва."""
    # Создаем отзыв
    data = {
        "name": "Иван Иванов",
        "company": "Tech Corp",
        "review_text": "Отличная работа!",
        "stars": 5
    }
    create_response = await client.post("/api/v1/reviews", json=data)
    review_id = create_response.json()["id"]
    
    # Обновляем отзыв
    update_data = {"stars": 4}
    response = await client.put(f"/api/v1/reviews/{review_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["stars"] == 4
