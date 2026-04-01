from typing import List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.db.models.seat import Seat

class SeatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, seat_id: uuid.UUID) -> Optional[Seat]:
        """Lấy thông tin ghế theo ID"""
        result = await self.session.execute(select(Seat).where(Seat.id == seat_id))
        return result.scalar_one_or_none()

    async def get_by_venue(self, venue_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Seat]:
        """Lấy danh sách ghế của một địa điểm có phân trang"""
        result = await self.session.execute(
            select(Seat)
            .where(Seat.venue_id == venue_id)
            .order_by(Seat.row_label, Seat.seat_number)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def check_exists(self, venue_id: uuid.UUID, row_label: str, seat_number: int) -> bool:
        """Kiểm tra ghế cụ thể đã tồn tại trong địa điểm chưa"""
        result = await self.session.execute(
            select(Seat)
            .where(
                Seat.venue_id == venue_id, 
                Seat.row_label == row_label, 
                Seat.seat_number == seat_number
            )
        )
        return result.scalar_one_or_none() is not None

    async def SeatCreate(self, seat: Seat) -> Seat:
        """Tạo ghế vật lý cho địa điểm"""
        self.session.add(seat)
        await self.session.flush()
        return seat

    async def SeatUpdate(self, seat: Seat) -> Seat:
        """Update ghế vật lý cho địa điểm"""
        await self.session.flush()
        return seat
    
    async def SeatDelete(self, seat: Seat) -> Seat:
        """Xoa ghế vật lý cho địa điểm"""
        await self.session.delete(seat)  # sửa self.session.delete(seat) => await self.session.delete(seat)
        await self.session.flush()
        return seat