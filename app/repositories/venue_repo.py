from typing import List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.db.models.venue import Venue

class VenueRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, venue_id: uuid.UUID) -> Optional[Venue]:
        """Lấy thông tin địa điểm theo ID"""
        result = await self.session.execute(select(Venue).where(Venue.id == venue_id))
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Venue]:
        """Lấy danh sách địa điểm có phân trang"""
        result = await self.session.execute(select(Venue).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, venue: Venue) -> Venue:
        """Tạo địa điểm mới (chưa commit)"""
        self.session.add(venue)
        await self.session.flush()
        return venue

    async def update(self, venue: Venue) -> Venue:
        """Cập nhật địa điểm (chưa commit)"""
        await self.session.flush()
        return venue

    async def delete(self, venue: Venue) -> Venue:
        """Xoá địa điểm (chưa commit)"""
        await self.session.delete(venue)
        await self.session.flush()
        return venue