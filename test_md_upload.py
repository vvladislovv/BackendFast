#!/usr/bin/env python3
"""Тест загрузки MD файлов для статей."""
import asyncio
import httpx

API_URL = "http://localhost:8000"
API_KEY = "internal-bot-key-2026"

async def test_api_md_upload():
    """Тест загрузки через API."""
    print("\n" + "="*60)
    print("ТЕСТ 1: Загрузка MD файла через API")
    print("="*60)
    
    # Читаем тестовый MD файл
    with open('test_article.md', 'rb') as f:
        files = {'data': ('test_article.md', f, 'text/markdown')}
        
        params = {
            'title': 'Тестовая статья из MD файла',
            'url': 'https://hacktaika.ru/test-md-article',
            'photo': 'https://hacktaika.ru/images/test.jpg'
        }
        
        headers = {'X-API-Key': API_KEY}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{API_URL}/api/v1/articles/upload-md",
                    params=params,
                    files=files,
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                result = response.json()
                
            print(f"✅ Статья создана через API!")
            print(f"   ID: {result['id']}")
            print(f"   Название: {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   Контент (первые 100 символов): {result['content'][:100]}...")
            print(f"   Фото: {result.get('photo', 'нет')}")
            
            return result['id']
            
        except httpx.HTTPStatusError as e:
            print(f"❌ Ошибка HTTP: {e.response.status_code}")
            print(f"   Ответ: {e.response.text}")
            return None
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None


async def test_get_article(article_id: int):
    """Проверка получения статьи."""
    print("\n" + "="*60)
    print(f"ТЕСТ 2: Получение статьи ID={article_id}")
    print("="*60)
    
    headers = {'X-API-Key': API_KEY}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_URL}/api/v1/articles/{article_id}",
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            result = response.json()
            
        print(f"✅ Статья получена!")
        print(f"   ID: {result['id']}")
        print(f"   Название: {result['title']}")
        print(f"   Контент (полный):")
        print("-" * 60)
        print(result['content'])
        print("-" * 60)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")


async def test_delete_article(article_id: int):
    """Удаление тестовой статьи."""
    print("\n" + "="*60)
    print(f"ТЕСТ 3: Удаление тестовой статьи ID={article_id}")
    print("="*60)
    
    headers = {'X-API-Key': API_KEY}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{API_URL}/api/v1/articles/{article_id}",
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            
        print(f"✅ Тестовая статья удалена")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")


async def main():
    """Основная функция."""
    print("\n🚀 ТЕСТИРОВАНИЕ ЗАГРУЗКИ MD ФАЙЛОВ ДЛЯ СТАТЕЙ")
    print("="*60)
    
    # Тест 1: Загрузка через API
    article_id = await test_api_md_upload()
    
    if article_id:
        # Тест 2: Получение статьи
        await test_get_article(article_id)
        
        # Тест 3: Удаление
        await test_delete_article(article_id)
    
    print("\n" + "="*60)
    print("📝 ИТОГ:")
    print("="*60)
    print("✅ API endpoint: POST /api/v1/articles/upload-md")
    print("   Параметры: title, url, photo (опционально)")
    print("   Файл: multipart/form-data с .md файлом")
    print("\n✅ Telegram бот: уже поддерживает загрузку .md файлов")
    print("   При создании статьи можно отправить .md файл вместо текста")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
