"""Сервис для работы с кейсами."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.case import Case
from schemas.case import CaseCreate, CaseUpdate
from utils.exceptions import NotFoundException
from utils.logger import get_logger

logger = get_logger()


class CaseService:
    """Сервис для CRUD операций с кейсами."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, data: CaseCreate) -> Case:
        """Создать кейс."""
        logger.info(f"Создание кейса: {data.name}")
        
        case_data = {k: v for k, v in data.model_dump(exclude_none=False).items() if v is not None}
        case = Case(**case_data)
        self.session.add(case)
        await self.session.commit()
        await self.session.refresh(case)
        
        logger.info(f"Кейс создан с ID: {case.id}")
        return case
    
    async def get_all(self, include_hidden: bool = False) -> list[Case]:
        """Получить все кейсы."""
        logger.info("Получение всех кейсов")
        
        query = select(Case).order_by(Case.rating.desc(), Case.created_at.desc())
        
        if not include_hidden:
            query = query.where(Case.is_hidden == False)
        
        result = await self.session.execute(query)
        cases = result.scalars().all()
        
        logger.info(f"Найдено кейсов: {len(cases)}")
        return list(cases)
    
    async def get_fresh(self) -> list[Case]:
        """Получить свежие кейсы."""
        logger.info("Получение свежих кейсов")
        
        query = select(Case).where(
            Case.is_fresh == True,
            Case.is_hidden == False
        ).order_by(Case.rating.desc(), Case.created_at.desc())
        
        result = await self.session.execute(query)
        cases = result.scalars().all()
        
        logger.info(f"Найдено свежих кейсов: {len(cases)}")
        return list(cases)

    async def get_by_id(self, case_id: int) -> Case:
        """Получить кейс по ID."""
        logger.info(f"Получение кейса с ID: {case_id}")
        
        result = await self.session.execute(
            select(Case).where(Case.id == case_id)
        )
        case = result.scalar_one_or_none()
        
        if not case:
            logger.error("Кейс с ID {} не найден", case_id)
            raise NotFoundException(f"Кейс с ID {case_id} не найден")
        
        return case
    
    async def update(self, case_id: int, data: CaseUpdate) -> Case:
        """Обновить кейс."""
        logger.info(f"Обновление кейса с ID: {case_id}")
        
        case = await self.get_by_id(case_id)
        
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(case, field, value)
        
        await self.session.commit()
        await self.session.refresh(case)
        
        logger.info(f"Кейс {case_id} обновлен")
        return case
    
    async def delete(self, case_id: int) -> None:
        """Удалить кейс."""
        logger.info(f"Удаление кейса с ID: {case_id}")
        
        case = await self.get_by_id(case_id)
        await self.session.delete(case)
        await self.session.commit()
        
        logger.info(f"Кейс {case_id} удален")
    
    async def toggle_hidden(self, case_id: int, is_hidden: bool) -> Case:
        """Скрыть/показать кейс."""
        logger.info(f"Изменение видимости кейса {case_id}: is_hidden={is_hidden}")
        
        case = await self.get_by_id(case_id)
        case.is_hidden = is_hidden
        
        await self.session.commit()
        await self.session.refresh(case)
        
        logger.info(f"Видимость кейса {case_id} изменена")
        return case
    
    async def update_rating(self, case_id: int, rating: int) -> Case:
        """Обновить рейтинг кейса."""
        logger.info(f"Обновление рейтинга кейса {case_id}: rating={rating}")
        
        case = await self.get_by_id(case_id)
        case.rating = rating
        
        await self.session.commit()
        await self.session.refresh(case)
        
        logger.info(f"Рейтинг кейса {case_id} обновлен")
        return case
    
    async def toggle_fresh(self, case_id: int, is_fresh: bool) -> Case:
        """Пометить кейс как свежий/обычный."""
        logger.info(f"Изменение статуса свежести кейса {case_id}: is_fresh={is_fresh}")
        
        case = await self.get_by_id(case_id)
        case.is_fresh = is_fresh
        
        await self.session.commit()
        await self.session.refresh(case)
        
        logger.info(f"Статус свежести кейса {case_id} изменен")
        return case
