from typing import List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.db.models.seat import Seat
from app.schemas.seat import SeatCreate, SeatUpdate
from app.repositories.seat_repo import SeatRepository
from app.repositories.venue_repo import VenueRepository

class SeatService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SeatRepository(session)
        self.venue_repo = VenueRepository(session)
        from app.repositories.showtime_seat_repo import ShowtimeSeatRepository
        self.showtime_seat_repo = ShowtimeSeatRepository(session)
    
    async def get_seats_by_showtime(self, showtime_id: uuid.UUID) -> List[any]:
        """Lấy danh sách ghế của một suất diễn cụ thể"""
        return await self.showtime_seat_repo.get_by_showtime_id(showtime_id)

    async def create_seat(self, venue_id: uuid.UUID, seat_data: SeatCreate) -> Seat:
        """Tạo ghế mới cho địa điểm"""
        # Kiểm tra xem venue có tồn tại không
        venue = await self.venue_repo.get_by_id(venue_id)
        if not venue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Venue not found"
            )
            
        # Kiểm tra ghế có bị trùng (UniqueConstraint)
        exists = await self.repo.check_exists(venue_id, seat_data.row_label, seat_data.seat_number)
        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Seat {seat_data.row_label}{seat_data.seat_number} already exists in this venue"
            )

        new_seat = Seat(
            venue_id=venue_id,
            row_label=seat_data.row_label,
            seat_number=seat_data.seat_number
        )
        created_seat = await self.repo.SeatCreate(new_seat)
        await self.session.commit()
        await self.session.refresh(created_seat)
        return created_seat

    async def get_seat(self, seat_id: uuid.UUID) -> Seat:
        """Lấy một ghế theo ID"""
        seat = await self.repo.get_by_id(seat_id)
        if not seat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Seat not found"
            )
        return seat

    async def get_seats_by_venue(self, venue_id: uuid.UUID, skip: int = 0, limit: int = 100) -> List[Seat]:
        """Lấy danh sách ghế của một địa điểm cụ thể"""
        # Kiểm tra venue trước khi lấy
        venue = await self.venue_repo.get_by_id(venue_id)
        if not venue:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Venue not found"
            )
            
        return await self.repo.get_by_venue(venue_id, skip=skip, limit=limit)

    async def update_seat(self, seat_id: uuid.UUID, seat_data: SeatUpdate) -> Seat:
        """Cập nhật ghế"""
        seat = await self.get_seat(seat_id)
        
        # Kiểm tra tính độc nhất nếu thay đổi row_label hoặc seat_number
        if seat_data.row_label is not None or seat_data.seat_number is not None:
            new_row = seat_data.row_label if seat_data.row_label is not None else seat.row_label
            new_num = seat_data.seat_number if seat_data.seat_number is not None else seat.seat_number
            
            # Chỉ kiểm tra nếu thực sự có thay đổi
            if new_row != seat.row_label or new_num != seat.seat_number:
                exists = await self.repo.check_exists(seat.venue_id, new_row, new_num)
                if exists:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, 
                        detail=f"Seat {new_row}{new_num} already exists in this venue"
                    )

        update_data = seat_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(seat, key, value)
            
        updated_seat = await self.repo.SeatUpdate(seat)
        await self.session.commit()
        await self.session.refresh(updated_seat)
        return updated_seat

    async def delete_seat(self, seat_id: uuid.UUID) -> None:
        """Xoá ghế"""
        seat = await self.get_seat(seat_id)
        await self.repo.SeatDelete(seat)
        await self.session.commit()