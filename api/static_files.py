"""Простой обработчик статических файлов."""
from pathlib import Path
from litestar import Controller, get
from litestar.response import File
from litestar.exceptions import NotFoundException
from utils.logger import get_logger

logger = get_logger()

class StaticFilesController(Controller):
    path = "/uploads"
    
    @get("/photos/{filename:str}")
    async def serve_photo(self, filename: str) -> File:
        """Отдает фотографии."""
        file_path = Path("uploads/photos") / filename
        
        logger.info(f"📁 Запрос фото: {filename}")
        logger.info(f"📂 Полный путь: {file_path.absolute()}")
        logger.info(f"✅ Файл существует: {file_path.exists()}")
        
        if not file_path.exists():
            logger.error(f"❌ Файл не найден: {file_path.absolute()}")
            raise NotFoundException(f"Файл {filename} не найден")
        
        logger.info(f"📤 Отдаем файл: {file_path.absolute()}")
        return File(
            path=file_path,
            filename=filename,
            content_disposition_type="inline"
        )