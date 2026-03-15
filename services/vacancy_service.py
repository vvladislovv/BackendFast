"""Сервис для работы с вакансиями."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.vacancy import Vacancy
from schemas.vacancy import VacancyCreate, VacancyUpdate
from utils.exceptions import NotFoundException
from utils.logger import get_logger

logger = get_logger()


class VacancyService:
    """Сервис для CRUD операций с вакансиями."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, data: VacancyCreate) -> Vacancy:
        """Создать вакансию."""
        logger.info(f"Создание вакансии: {data.title}, rating={data.rating}")
        
        try:
            vacancy_data = {k: v for k, v in data.model_dump(exclude_none=False).items() if v is not None}
            logger.info(f"Данные для создания: {vacancy_data}")
            vacancy = Vacancy(**vacancy_data)
            self.session.add(vacancy)
            await self.session.commit()
            await self.session.refresh(vacancy)
            
            logger.info(f"Вакансия создана с ID: {vacancy.id}, rating={vacancy.rating}")
            return vacancy
        except Exception as e:
            logger.error(f"Ошибка при создании вакансии: {e}", exc_info=True)
            await self.session.rollback()
            raise
    
    async def get_all(self, include_hidden: bool = False) -> list[Vacancy]:
        """Получить все вакансии."""
        logger.info(f"Получение всех вакансий, include_hidden={include_hidden}")
        
        query = select(Vacancy).order_by(Vacancy.rating.desc(), Vacancy.created_at.desc())
        
        if not include_hidden:
            query = query.where(Vacancy.is_hidden == False)
            logger.info("Фильтруем скрытые вакансии")
        else:
            logger.info("Включаем скрытые вакансии")
        
        result = await self.session.execute(query)
        vacancies = result.scalars().all()
        
        logger.info(f"Найдено вакансий: {len(vacancies)}")
        for vacancy in vacancies:
            logger.info(f"Вакансия ID {vacancy.id}: is_hidden={vacancy.is_hidden}")
        
        return list(vacancies)

    async def get_by_id(self, vacancy_id: int) -> Vacancy:
        """Получить вакансию по ID."""
        logger.info(f"Получение вакансии с ID: {vacancy_id}")
        
        result = await self.session.execute(
            select(Vacancy).where(Vacancy.id == vacancy_id)
        )
        vacancy = result.scalar_one_or_none()
        
        if not vacancy:
            logger.error("Вакансия с ID {} не найдена", vacancy_id)
            raise NotFoundException(f"Вакансия с ID {vacancy_id} не найдена")
        
        return vacancy
    
    async def update(self, vacancy_id: int, data: VacancyUpdate) -> Vacancy:
        """Обновить вакансию."""
        logger.info(f"Обновление вакансии с ID: {vacancy_id}")
        
        vacancy = await self.get_by_id(vacancy_id)
        
        update_data = data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(vacancy, field, value)
        
        await self.session.commit()
        await self.session.refresh(vacancy)
        
        logger.info(f"Вакансия {vacancy_id} обновлена")
        return vacancy
    
    async def delete(self, vacancy_id: int) -> None:
        """Удалить вакансию."""
        logger.info(f"Удаление вакансии с ID: {vacancy_id}")
        
        vacancy = await self.get_by_id(vacancy_id)
        await self.session.delete(vacancy)
        await self.session.commit()
        
        logger.info(f"Вакансия {vacancy_id} удалена")
    
    async def toggle_hidden(self, vacancy_id: int, is_hidden: bool) -> Vacancy:
        """Скрыть/показать вакансию."""
        logger.info(f"Изменение видимости вакансии {vacancy_id}: is_hidden={is_hidden}")
        
        vacancy = await self.get_by_id(vacancy_id)
        vacancy.is_hidden = is_hidden
        
        await self.session.commit()
        await self.session.refresh(vacancy)
        
        logger.info(f"Видимость вакансии {vacancy_id} изменена")
        return vacancy
    
    async def update_rating(self, vacancy_id: int, rating: int) -> Vacancy:
        """Обновить рейтинг вакансии."""
        logger.info(f"Обновление рейтинга вакансии {vacancy_id}: rating={rating}")
        
        vacancy = await self.get_by_id(vacancy_id)
        vacancy.rating = rating
        
        await self.session.commit()
        await self.session.refresh(vacancy)
        
        logger.info(f"Рейтинг вакансии {vacancy_id} обновлен")
        return vacancy
