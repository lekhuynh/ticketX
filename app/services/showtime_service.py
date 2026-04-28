from typing import List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.db.models.showtime import Showtime
from app.schemas.showtime import ShowtimeCreate, ShowtimeUpdate
from app.repositories.showtime_repo import ShowtimeRepository
from app.repositories.event_repo import EventsRepository

class ShowtimeService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ShowtimeRepository(session)
        self.event_repo = EventsRepository(session)

    async def create_showtime(self, showtime_data: ShowtimeCreate) -> Showtime:
        """Tạo suất diễn mới"""
        # Kiểm tra sự kiện có tồn tại không
        event = await self.event_repo.get_event_by_id(showtime_data.event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        # Kiểm tra trùng lặp thời gian suất diễn
        is_overlapping = await self.repo.check_overlapping(
            showtime_data.event_id, 
            showtime_data.start_time, 
            showtime_data.end_time
        )
        if is_overlapping:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Showtime overlaps with another showtime for this event"
            )

        new_showtime = Showtime(
            event_id=showtime_data.event_id,
            start_time=showtime_data.start_time,
            end_time=showtime_data.end_time
        )
        
        created_showtime = await self.repo.create(new_showtime)
        await self.session.commit()
        await self.session.refresh(created_showtime)
        return created_showtime

    async def get_showtime(self, showtime_id: uuid.UUID) -> Showtime:
        """Lấy thông tin một suất diễn"""
        showtime = await self.repo.get_by_id(showtime_id)
        if not showtime:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Showtime not found"
            )
        return showtime

    async def get_showtimes_by_event(self, event_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Showtime]:
        """Lấy danh sách suất diễn của một sự kiện"""
        # Xác minh sự kiện trước
        event = await self.event_repo.get_event_by_id(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )
        return await self.repo.get_by_event(event_id, skip=skip, limit=limit)

    async def update_showtime(self, showtime_id: uuid.UUID, showtime_data: ShowtimeUpdate) -> Showtime:
        """Cập nhật suất diễn"""
        showtime = await self.get_showtime(showtime_id)
        
        # Determine new start and end times for validation
        new_start = showtime_data.start_time if showtime_data.start_time else showtime.start_time
        new_end = showtime_data.end_time if showtime_data.end_time else showtime.end_time
        
        # Only check overlap if times are actually changing
        if showtime_data.start_time or showtime_data.end_time:
            if new_end <= new_start:
                 raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="end_time must be after start_time"
                 )
                 
            is_overlapping = await self.repo.check_overlapping(
                showtime.event_id, 
                new_start, 
                new_end, 
                exclude_id=showtime.id
            )
            if is_overlapping:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Updated times overlap with another showtime"
                )

        update_data = showtime_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(showtime, key, value)
            
        updated_showtime = await self.repo.update(showtime)
        await self.session.commit()
        await self.session.refresh(updated_showtime)
        return updated_showtime

    async def delete_showtime(self, showtime_id: uuid.UUID) -> None:
        """Xoá suất diễn"""
        showtime = await self.get_showtime(showtime_id)
        await self.repo.delete(showtime)
        await self.session.commit()

