"""API endpoints для статей."""
from litestar import Controller, get, post, put, delete, patch
from litestar.di import Provide
from litestar.params import Dependency, Parameter
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session
from schemas.article import (
    ArticleCreate,
    ArticleUpdate,
    ArticleResponse,
    ArticleHideUpdate,
    ArticleRatingUpdate,
)
from services.article_service import ArticleService
from utils.logger import get_logger

logger = get_logger()


async def get_article_service(
    db_session: AsyncSession = Dependency(skip_validation=True),
) -> ArticleService:
    """Dependency для получения сервиса статей."""
    return ArticleService(db_session)


class ArticleController(Controller):
    """Контроллер для работы со статьями."""

    path = "/api/v1/articles"
    tags = ["Articles"]
    dependencies = {"article_service": Provide(get_article_service)}

    @post(
        "/",
        summary="Создать статью",
        description="Создает новую статью или публикацию",
        status_code=201,
    )
    async def create_article(
        self,
        data: ArticleCreate,
        article_service: ArticleService,
    ) -> ArticleResponse:
        """Создать новую статью."""
        logger.info("POST /api/v1/articles - создание статьи")
        article = await article_service.create(data)
        return ArticleResponse.model_validate(article)

    @get(
        "/",
        summary="Получить список статей",
        description="Возвращает список всех статей, отсортированных по рейтингу",
    )
    async def get_articles(
        self,
        article_service: ArticleService,
        include_hidden: bool = False,
    ) -> list[ArticleResponse]:
        """Получить все статьи."""
        logger.info("GET /api/v1/articles - получение всех статей")
        articles = await article_service.get_all(include_hidden=include_hidden)
        return [ArticleResponse.model_validate(a) for a in articles]

    @get(
        "/{article_id:int}",
        summary="Получить статью по ID",
        description="Возвращает одну статью по её ID",
    )
    async def get_article(
        self,
        article_id: int,
        article_service: ArticleService,
    ) -> ArticleResponse:
        """Получить статью по ID."""
        logger.info(f"GET /api/v1/articles/{article_id}")
        article = await article_service.get_by_id(article_id)
        return ArticleResponse.model_validate(article)

    @put(
        "/{article_id:int}",
        summary="Обновить статью",
        description="Обновляет существующую статью. Все поля опциональны",
    )
    async def update_article(
        self,
        article_id: int,
        data: ArticleUpdate,
        article_service: ArticleService,
    ) -> ArticleResponse:
        """Обновить статью."""
        logger.info(f"PUT /api/v1/articles/{article_id}")
        article = await article_service.update(article_id, data)
        return ArticleResponse.model_validate(article)

    @delete(
        "/{article_id:int}",
        summary="Удалить статью",
        description="Удаляет статью из системы безвозвратно",
        status_code=200,
    )
    async def delete_article(
        self,
        article_id: int,
        article_service: ArticleService,
    ) -> dict[str, str]:
        """Удалить статью."""
        logger.info(f"DELETE /api/v1/articles/{article_id}")
        await article_service.delete(article_id)
        return {"message": "Статья успешно удалена"}

    @patch(
        "/{article_id:int}/hide",
        summary="Скрыть/показать статью",
        description="Изменяет видимость статьи без удаления",
    )
    async def toggle_article_hidden(
        self,
        article_id: int,
        article_service: ArticleService,
        is_hidden: bool | None = Parameter(default=None, query="is_hidden"),
    ) -> ArticleResponse:
        """Скрыть/показать статью."""
        logger.info(f"PATCH /api/v1/articles/{article_id}/hide")
        
        if is_hidden is None:
            article = await article_service.get_by_id(article_id)
            is_hidden = not article.is_hidden
        
        article = await article_service.toggle_hidden(article_id, is_hidden)
        return ArticleResponse.model_validate(article)

    @patch(
        "/{article_id:int}/rating",
        summary="Обновить рейтинг статьи",
        description="Изменяет рейтинг статьи для сортировки",
    )
    async def update_article_rating(
        self,
        article_id: int,
        article_service: ArticleService,
        rating: int = Parameter(default=1, query="rating"),
    ) -> ArticleResponse:
        """Обновить рейтинг статьи."""
        logger.info(f"PATCH /api/v1/articles/{article_id}/rating")
        article = await article_service.update_rating(article_id, rating)
        return ArticleResponse.model_validate(article)

