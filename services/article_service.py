"""Сервис для работы со статьями."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.article import Article
from schemas.article import ArticleCreate, ArticleUpdate
from utils.exceptions import NotFoundException
from utils.logger import get_logger

logger = get_logger()


class ArticleService:
    """Сервис для CRUD операций со статьями."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, data: ArticleCreate) -> Article:
        """Создать статью."""
        logger.info(f"Создание статьи: {data.title}")
        
        article = Article(**data.model_dump())
        self.session.add(article)
        await self.session.commit()
        await self.session.refresh(article)
        
        logger.info(f"Статья создана с ID: {article.id}")
        return article
    
    async def get_all(self, include_hidden: bool = False) -> list[Article]:
        """Получить все статьи."""
        logger.info("Получение всех статей")
        
        query = select(Article).order_by(Article.rating.desc(), Article.created_at.desc())
        
        if not include_hidden:
            query = query.where(Article.is_hidden == False)
        
        result = await self.session.execute(query)
        articles = result.scalars().all()
        
        logger.info(f"Найдено статей: {len(articles)}")
        return list(articles)
    
    async def get_by_id(self, article_id: int) -> Article:
        """Получить статью по ID."""
        logger.info(f"Получение статьи с ID: {article_id}")
        
        result = await self.session.execute(
            select(Article).where(Article.id == article_id)
        )
        article = result.scalar_one_or_none()
        
        if not article:
            logger.error(f"Статья с ID {article_id} не найдена")
            raise NotFoundException(f"Статья с ID {article_id} не найдена")
        
        return article

    async def update(self, article_id: int, data: ArticleUpdate) -> Article:
        """Обновить статью."""
        logger.info(f"Обновление статьи с ID: {article_id}")
        
        article = await self.get_by_id(article_id)
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(article, field, value)
        
        await self.session.commit()
        await self.session.refresh(article)
        
        logger.info(f"Статья {article_id} обновлена")
        return article
    
    async def delete(self, article_id: int) -> None:
        """Удалить статью."""
        logger.info(f"Удаление статьи с ID: {article_id}")
        
        article = await self.get_by_id(article_id)
        await self.session.delete(article)
        await self.session.commit()
        
        logger.info(f"Статья {article_id} удалена")
    
    async def toggle_hidden(self, article_id: int, is_hidden: bool) -> Article:
        """Скрыть/показать статью."""
        logger.info(f"Изменение видимости статьи {article_id}: is_hidden={is_hidden}")
        
        article = await self.get_by_id(article_id)
        article.is_hidden = is_hidden
        
        await self.session.commit()
        await self.session.refresh(article)
        
        logger.info(f"Видимость статьи {article_id} изменена")
        return article
    
    async def update_rating(self, article_id: int, rating: int) -> Article:
        """Обновить рейтинг статьи."""
        logger.info(f"Обновление рейтинга статьи {article_id}: rating={rating}")
        
        article = await self.get_by_id(article_id)
        article.rating = rating
        
        await self.session.commit()
        await self.session.refresh(article)
        
        logger.info(f"Рейтинг статьи {article_id} обновлен")
        return article
