from typing import List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.db.models.venue import Venue
from app.schemas.venue import VenueCreate, VenueUpdate
from app.repositories.venue_repo import VenueRepository

class VenueService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = VenueRepository(session)

    async def create_venue(self, venue_data: VenueCreate) -> Venue:
        """Tạo địa điểm mới"""
        new_venue = Venue(
            name=venue_data.name,
            address=venue_data.address,
            capacity=venue_data.capacity
        )
        created_venue = await self.repo.create(new_venue)
        await self.session.commit()
        await self.session.refresh(created_venue)
        return created_venue

    async def get_venue(self, venue_id: uuid.UUID) -> Venue:
        """Lấy thông tin địa điểm theo ID"""
        venue = await self.repo.get_by_id(venue_id)
        if not venue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Venue not found"
            )
        return venue

    async def get_venues(self, skip: int = 0, limit: int = 100) -> List[Venue]:
        """Lấy danh sách địa điểm"""
        return await self.repo.get_all(skip=skip, limit=limit)

    async def update_venue(self, venue_id: uuid.UUID, venue_data: VenueUpdate) -> Venue:
        """Cập nhật thông tin địa điểm"""
        venue = await self.get_venue(venue_id)
        
        # Cập nhật các trường được truyền lên
        update_data = venue_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(venue, key, value)
            
        updated_venue = await self.repo.update(venue)
        await self.session.commit()
        await self.session.refresh(updated_venue)
        return updated_venue

    async def delete_venue(self, venue_id: uuid.UUID) -> None:
        """Xoá địa điểm"""
        venue = await self.get_venue(venue_id)
        await self.repo.delete(venue)
        await self.session.commit()

    async def get_all_venue(self, skip: int = 0, limit :int = 100) -> List[Venue]:
        result = await self.repo.get_all(skip=skip, limit=limit)
        return list(result)