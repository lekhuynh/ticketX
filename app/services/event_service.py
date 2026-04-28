from typing import List
import uuid
from fastapi import HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.db.models.event import Event
from app.schemas.event import EventCreate, EventUpdate
from app.repositories.event_repo import EventsRepository
from app.repositories.venue_repo import VenueRepository

class EventService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo_event = EventsRepository(session)
        self.repo_venue = VenueRepository(session)

    async def create_event(self, venue_id: uuid.UUID, event_data: EventCreate) -> Event:
        """Tạo sự kiện cho ban tổ chức"""
        # Kiểm tra xem venue_id có tồn tại không
        venue = await self.repo_venue.get_by_id(venue_id)
        if not venue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Venue not found"
            ) 
        
        # Kiểm tra xem có bị trùng tên không 
        exists = await self.repo_event.check_exists(venue_id, event_data.name )
        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Trùng tên rồi"
            )
        new_event = Event(
            venue_id=venue_id,
            name=event_data.name,
            description=event_data.description,
            image_url=event_data.image_url,
            category=event_data.category,
        )
        result = await self.repo_event.create_event(new_event)
        await self.session.commit()
        await self.session.refresh(result)
        return result

    async def get_event(self, event_id: uuid.UUID) -> Event:
        result = await self.repo_event.get_by_id(event_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail= "Event not found"
            )
        return result

    async def get_all_event(self, skip: int = 0, limit: int =100) -> List[Event]:
        result = await self.repo_event.get_all_event(skip=skip, limit=limit)
        return list(result)

    async def update_event(self,event_id: uuid.UUID, data_event: EventUpdate) -> Event:
        """Update event"""

        #Check id hợp lệ không
        event = await self.get_event(event_id)

        if data_event.name is not None and data_event.name != event.name:
            exists = await self.repo_event.check_exists(event.venue_id, data_event.name )
            if exists:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Tên sự kiện mới bị trùng với một sự kiện khác trong rạp này!"
                )

        # Cập nhật các trường được truyền lên
        new_event = data_event.model_dump(exclude_unset= True)
        for key, value in new_event.items():
            setattr(event, key, value)

        result = await self.repo_event.update_event(event)
        await self.session.commit()
        await self.session.refresh(result)
        return result

    async def delete_event(self, event_id: uuid.UUID) -> None:
        delete_event = await self.get_event(event_id)
        await self.repo_event.delete_event(delete_event)
        await self.session.commit()