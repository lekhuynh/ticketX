from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.event import Event
from app.schemas.event import EventCreate, EventResponse, EventUpdate
import uuid

class EventsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_event(self, event: Event) -> Event:
        """tao event moi"""
        self.session.add(event)
        await self.session.flush()
        return event

    async def update_event(self, event: Event) -> Event:
        """Update event"""
        await self.session.flush()
        return event

    async def delete_event(self, event: Event) -> Event:
        await self.session.delete(event)
        await self.session.flush()
        return event

    async def get_by_id(self, event_id: uuid.UUID) -> Event | None:
        result = await self.session.execute(
            select(Event)
            .where(Event.id == event_id)
            .options(selectinload(Event.venue), selectinload(Event.showtimes))
        )
        return result.scalar_one_or_none()

    async def get_all_event(self, skip: int = 0, limit: int = 100) -> List[Event]:
        result = await self.session.execute(
            select(Event)
            .offset(skip)
            .limit(limit)
            .options(selectinload(Event.venue), selectinload(Event.showtimes))
        )
        return list(result.scalars().all())

    async def check_exists(self, venue_id:uuid.UUID, name: str ) -> bool:
        """Kiểm tra xem Rạp này đã có sự kiện nào mang tên này chưa"""
        result = await self.session.execute(select(Event)
        .where(
            Event.venue_id == venue_id,
            Event.name == name
         ))
        return result.scalar_one_or_none() is not None