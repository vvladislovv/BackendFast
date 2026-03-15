"""Обработчик фотографий для телеграм бота."""
import os
import uuid
import httpx
from pathlib import Path
from aiogram import Bot
from utils.logger import get_logger

logger = get_logger()

# Директория для сохранения фотографий
PHOTOS_DIR = Path("uploads/photos")
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

# URL для доступа к фотографиям - используем переменную окружения или localhost
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")
PHOTOS_BASE_URL = f"{API_BASE_URL}/uploads/photos"

async def download_and_save_photo(bot: Bot, file_id: str) -> str:
    """
    Скачивает фото из Telegram и сохраняет на сервере.
    Возвращает HTTP URL для доступа к фото.
    """
    try:
        logger.info(f"🔄 Начинаем обработку фото с File ID: {file_id}")
        
        # Убеждаемся что директория существует
        PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"📂 Директория создана/проверена: {PHOTOS_DIR.absolute()}")
        
        # Получаем информацию о файле
        file_info = await bot.get_file(file_id)
        logger.info(f"📁 Telegram путь файла: {file_info.file_path}")
        
        # Генерируем уникальное имя файла
        file_extension = Path(file_info.file_path).suffix or '.jpg'
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        local_path = PHOTOS_DIR / unique_filename
        
        logger.info(f"💾 Сохраняем в: {local_path.absolute()}")
        
        # Скачиваем файл из Telegram
        file_url = f"https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}"
        logger.info(f"🌐 Скачиваем с Telegram: {file_url}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(file_url, timeout=30.0)
            response.raise_for_status()
            
            # Сохраняем файл на диск
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            # Проверяем что файл сохранился
            if local_path.exists():
                file_size = local_path.stat().st_size
                logger.info(f"✅ Файл успешно сохранен: {local_path.absolute()}")
                logger.info(f"📏 Размер файла: {file_size} байт")
                
                # Проверяем права доступа
                logger.info(f"🔐 Права доступа: {oct(local_path.stat().st_mode)}")
            else:
                logger.error(f"❌ Файл не был сохранен: {local_path.absolute()}")
                return f"tg://photo/{file_id}"
        
        # Формируем HTTP URL для доступа
        photo_url = f"{PHOTOS_BASE_URL}/{unique_filename}"
        
        logger.info(f"📷 ФОТО УСПЕШНО ОБРАБОТАНО:")
        logger.info(f"   🆔 File ID: {file_id}")
        logger.info(f"   📁 Telegram путь: {file_info.file_path}")
        logger.info(f"   💾 Локальный путь: {local_path.absolute()}")
        logger.info(f"   📏 Размер: {len(response.content)} байт")
        logger.info(f"   🔗 HTTP URL: {photo_url}")
        logger.info(f"   ✅ Файл доступен: {local_path.exists()}")
        
        return photo_url
        
    except Exception as e:
        logger.error(f"❌ ОШИБКА при сохранении фото {file_id}: {e}", exc_info=True)
        # Возвращаем fallback URL
        fallback_url = f"tg://photo/{file_id}"
        logger.info(f"🔄 Возвращаем fallback URL: {fallback_url}")
        return fallback_url


def test_photo_access():
    """Тестирует доступ к сохраненным фотографиям."""
    logger.info("🧪 Тестируем доступ к фотографиям...")
    
    # Создаем тестовый файл
    test_file = PHOTOS_DIR / "test_access.txt"
    test_content = "Test photo access"
    
    try:
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        logger.info(f"✅ Тестовый файл создан: {test_file.absolute()}")
        logger.info(f"🔗 Должен быть доступен по: {PHOTOS_BASE_URL}/test_access.txt")
        
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка создания тестового файла: {e}")
        return False