"""API endpoints для статей."""
from litestar import Controller, get, post, put, delete, patch
from litestar.di import Provide
from litestar.params import Dependency
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session
from schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse, ArticleHideUpdate, ArticleRatingUpdate
from services.article_service import ArticleService
from utils.logger import get_logger

logger = get_logger()


async def get_article_service(db_session: AsyncSession = Dependency(skip_validation=True)) -> ArticleService:
    return ArticleService(db_session)


class ArticleController(Controller):
    path = "/api/v1/articles"
    tags = ["Articles"]
    dependencies = {"article_service": Provide(get_article_service)}

    @post("/", summary="Создать статью", description="Создание новой статьи. **Параметры (JSON):** title (обязательно, 1-255 символов), content (обязательно), author (опционально, до 255 символов). **Требуется API ключ**", status_code=201)
    async def create_article(self, data: ArticleCreate, article_service: ArticleService) -> ArticleResponse:
        logger.info("POST /api/v1/articles")
        article = await article_service.create(data)
        return ArticleResponse.model_validate(article)

    @get("/", summary="Получить список статей", description="Получение всех видимых статей (is_hidden=false). **Требуется API ключ**")
    async def get_articles(self, article_service: ArticleService) -> list[ArticleResponse]:
        logger.info("GET /api/v1/articles")
        articles = await article_service.get_all(include_hidden=False)
        return [ArticleResponse.model_validate(a) for a in articles]

    @get("/{article_id:int}", summary="Получить статью", description="Получение статьи по ID. **Параметр пути:** article_id. **Требуется API ключ**")
    async def get_article(self, article_id: int, article_service: ArticleService) -> ArticleResponse:
        logger.info(f"GET /api/v1/articles/{article_id}")
        article = await article_service.get_by_id(article_id)
        return ArticleResponse.model_validate(article)

    @put("/{article_id:int}", summary="Обновить статью", description="Обновление статьи. **Параметр пути:** article_id. **Параметры (JSON):** title, content, author (все опциональны). **Требуется API ключ**")
    async def update_article(self, article_id: int, data: ArticleUpdate, article_service: ArticleService) -> ArticleResponse:
        logger.info(f"PUT /api/v1/articles/{article_id}")
        article = await article_service.update(article_id, data)
        return ArticleResponse.model_validate(article)

    @delete("/{article_id:int}", summary="Удалить статью", description="Удаление статьи. **Параметр пути:** article_id. **Требуется API ключ**", status_code=200)
    async def delete_article(self, article_id: int, article_service: ArticleService) -> dict[str, str]:
        logger.info(f"DELETE /api/v1/articles/{article_id}")
        await article_service.delete(article_id)
        return {"message": "Статья удалена"}

    @patch("/{article_id:int}/hide", summary="Скрыть/показать статью", description="Изменение видимости. **Параметр пути:** article_id. **Параметр (JSON):** is_hidden (true/false). **Требуется API ключ**")
    async def toggle_article_hidden(self, article_id: int, data: ArticleHideUpdate, article_service: ArticleService) -> ArticleResponse:
        logger.info(f"PATCH /api/v1/articles/{article_id}/hide")
        article = await article_service.toggle_hidden(article_id, data.is_hidden)
        return ArticleResponse.model_validate(article)

    @patch("/{article_id:int}/rating", summary="Обновить рейтинг", description="Изменение рейтинга статьи. **Параметр пути:** article_id. **Параметр (JSON):** rating (целое число). **Требуется API ключ**")
    async def update_article_rating(self, article_id: int, data: ArticleRatingUpdate, article_service: ArticleService) -> ArticleResponse:
        logger.info(f"PATCH /api/v1/articles/{article_id}/rating")
        article = await article_service.update_rating(article_id, data.rating)
        return ArticleResponse.model_validate(article)
