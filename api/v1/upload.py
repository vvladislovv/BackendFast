"""API endpoints для загрузки файлов."""
import os
import uuid
from pathlib import Path
from litestar import Controller, post
from litestar.datastructures import UploadFile
from litestar.enums import RequestEncodingType
from litestar.params import Body

from utils.logger import get_logger

logger = get_logger()

# Директория для хранения файлов
UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class UploadController(Controller):
    """Контроллер для загрузки файлов."""
    
    path = "/api/v1/upload"
    tags = ["Upload"]
    
    @post(
        "/",
        summary="Загрузить файл",
        description="Загрузка файла на сервер. Возвращает путь к файлу.",
        status_code=201,
    )
    async def upload_file(
        self,
        data: UploadFile = Body(media_type=RequestEncodingType.MULTI_PART),
    ) -> dict[str, str]:
        """Загрузить файл."""
        try:
            logger.info(f"Загрузка файла: {data.filename}")
            
            # Генерируем уникальное имя файла
            file_ext = Path(data.filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = UPLOAD_DIR / unique_filename
            
            # Сохраняем файл
            content = await data.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            logger.info(f"Файл сохранен: {file_path}")
            
            return {
                "filename": unique_filename,
                "original_filename": data.filename,
                "path": str(file_path),
                "size": len(content)
            }
            
        except Exception as e:
            logger.error(f"Ошибка загрузки файла: {e}", exc_info=True)
            raise
