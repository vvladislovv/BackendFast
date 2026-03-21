"""Тестирование статей с Markdown контентом."""
import requests

API_URL = "http://localhost:8000"
API_KEY = "internal-bot-key-2026"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

# Тестовый Markdown контент
markdown_content = """# Заголовок статьи

Это **жирный текст** и *курсив*.

## Подзаголовок

- Пункт списка 1
- Пункт списка 2
- Пункт списка 3

### Код

```python
def hello():
    print("Hello, World!")
```

[Ссылка на сайт](https://example.com)
"""

def test_create_article():
    """Тест создания статьи с Markdown."""
    print("🧪 Тест 1: Создание статьи с Markdown контентом")
    
    payload = {
        "title": "Тестовая статья с Markdown",
        "url": "https://example.com/test-article",
        "content": markdown_content,
        "photo": "https://example.com/photo.jpg"
    }
    
    response = requests.post(f"{API_URL}/api/v1/articles", json=payload, headers=HEADERS)
    
    if response.status_code == 201:
        article = response.json()
        print(f"✅ Статья создана! ID: {article['id']}")
        print(f"   Название: {article['title']}")
        print(f"   URL: {article['url']}")
        print(f"   Контент (первые 100 символов): {article['content'][:100]}...")
        print(f"   Фото: {article.get('photo', 'Нет')}")
        return article['id']
    else:
        print(f"❌ Ошибка: {response.status_code}")
        print(f"   {response.text}")
        return None


def test_get_article(article_id):
    """Тест получения статьи."""
    print(f"\n🧪 Тест 2: Получение статьи ID {article_id}")
    
    response = requests.get(f"{API_URL}/api/v1/articles/{article_id}", headers=HEADERS)
    
    if response.status_code == 200:
        article = response.json()
        print(f"✅ Статья получена!")
        print(f"   Название: {article['title']}")
        print(f"   Контент:\n{article['content']}")
        return True
    else:
        print(f"❌ Ошибка: {response.status_code}")
        return False


def test_update_article(article_id):
    """Тест обновления контента статьи."""
    print(f"\n🧪 Тест 3: Обновление контента статьи ID {article_id}")
    
    new_content = """# Обновленный заголовок

Это **обновленный** контент статьи.

## Новый раздел

1. Первый пункт
2. Второй пункт
3. Третий пункт
"""
    
    payload = {"content": new_content}
    response = requests.put(f"{API_URL}/api/v1/articles/{article_id}", json=payload, headers=HEADERS)
    
    if response.status_code == 200:
        article = response.json()
        print(f"✅ Контент обновлен!")
        print(f"   Новый контент:\n{article['content']}")
        return True
    else:
        print(f"❌ Ошибка: {response.status_code}")
        print(f"   {response.text}")
        return False


def test_get_all_articles():
    """Тест получения всех статей."""
    print(f"\n🧪 Тест 4: Получение всех статей")
    
    response = requests.get(f"{API_URL}/api/v1/articles", headers=HEADERS)
    
    if response.status_code == 200:
        articles = response.json()
        print(f"✅ Получено статей: {len(articles)}")
        for article in articles:
            print(f"   - ID {article['id']}: {article['title']}")
            print(f"     Контент (первые 50 символов): {article['content'][:50]}...")
        return True
    else:
        print(f"❌ Ошибка: {response.status_code}")
        return False


def test_delete_article(article_id):
    """Тест удаления статьи."""
    print(f"\n🧪 Тест 5: Удаление статьи ID {article_id}")
    
    response = requests.delete(f"{API_URL}/api/v1/articles/{article_id}", headers=HEADERS)
    
    if response.status_code == 200:
        print(f"✅ Статья удалена!")
        return True
    else:
        print(f"❌ Ошибка: {response.status_code}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ СТАТЕЙ С MARKDOWN КОНТЕНТОМ")
    print("=" * 60)
    
    # Создаем статью
    article_id = test_create_article()
    
    if article_id:
        # Получаем статью
        test_get_article(article_id)
        
        # Обновляем контент
        test_update_article(article_id)
        
        # Получаем все статьи
        test_get_all_articles()
        
        # Удаляем тестовую статью
        test_delete_article(article_id)
    
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)
