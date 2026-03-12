"""Тесты для API статей."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_article(client: AsyncClient):
    """Тест создания статьи."""
    data = {
        "title": "Новая статья",
        "url": "https://example.com/article",
        "photo_url": "https://example.com/photo.jpg"
    }
    
    response = await client.post("/api/v1/articles", json=data)
    assert response.status_code == 201
    assert response.json()["title"] == data["title"]


@pytest.mark.asyncio
async def test_get_articles(client: AsyncClient):
    """Тест получения всех статей."""
    response = await client.get("/api/v1/articles")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_delete_article(client: AsyncClient):
    """Тест удаления статьи."""
    # Создаем статью
    data = {
        "title": "Статья для удаления",
        "url": "https://example.com/article"
    }
    create_response = await client.post("/api/v1/articles", json=data)
    article_id = create_response.json()["id"]
    
    # Удаляем статью
    response = await client.delete(f"/api/v1/articles/{article_id}")
    assert response.status_code == 200
    
    # Проверяем что статья удалена
    get_response = await client.get(f"/api/v1/articles/{article_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_toggle_article_hidden(client: AsyncClient):
    """Тест скрытия/показа статьи."""
    # Создаем статью
    data = {
        "title": "Статья",
        "url": "https://example.com/article"
    }
    create_response = await client.post("/api/v1/articles", json=data)
    article_id = create_response.json()["id"]
    
    # Скрываем статью
    response = await client.patch(
        f"/api/v1/articles/{article_id}/hide",
        json={"is_hidden": True}
    )
    assert response.status_code == 200
    assert response.json()["is_hidden"] is True
