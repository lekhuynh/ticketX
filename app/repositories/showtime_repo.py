from typing import List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.db.models.showtime import Showtime

class ShowtimeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, showtime_id: uuid.UUID) -> Optional[Showtime]:
        """Lấy thông tin suất diễn theo ID"""
        result = await self.session.execute(select(Showtime).where(Showtime.id == showtime_id))
        return result.scalar_one_or_none()

    async def get_by_event(self, event_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Showtime]:
        """Lấy danh sách suất diễn của một sự kiện"""
        result = await self.session.execute(
            select(Showtime)
            .where(Showtime.event_id == event_id)
            .order_by(Showtime.start_time)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def check_overlapping(self, event_id: uuid.UUID, start_time, end_time, exclude_id: Optional[uuid.UUID] = None) -> bool:
        """Kiểm tra xem suất diễn có bị trùng lấp thời gian với suất diễn khác của cùng sự kiện không"""
        query = select(Showtime).where(
            Showtime.event_id == event_id,
            Showtime.start_time < end_time,
            Showtime.end_time > start_time
        )
        if exclude_id:
            query = query.where(Showtime.id != exclude_id)
            
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def create(self, showtime: Showtime) -> Showtime:
        """Tạo suất diễn mới (chưa commit)"""
        self.session.add(showtime)
        await self.session.flush()
        return showtime

    async def update(self, showtime: Showtime) -> Showtime:
        """Cập nhật suất diễn (chưa commit)"""
        await self.session.flush()
        return showtime

    async def delete(self, showtime: Showtime) -> Showtime:
        """Xoá suất diễn (chưa commit)"""
        await self.session.delete(showtime)
        await self.session.flush()
        return showtime
