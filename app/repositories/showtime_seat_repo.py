import uuid
from typing import List, Sequence
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import StaleDataError

from app.db.models.showtime_seat import ShowtimeSeat
from app.db.models.enums import SeatStatus

class ShowtimeSeatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_by_showtime_id(self, showtime_id: uuid.UUID) -> Sequence[ShowtimeSeat]:
        from sqlalchemy.orm import selectinload
        stmt = select(ShowtimeSeat).where(
            ShowtimeSeat.showtime_id == showtime_id
        ).options(selectinload(ShowtimeSeat.seat))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_seats_by_ids(self, showtime_id: uuid.UUID, showtime_seat_ids: List[uuid.UUID]) -> Sequence[ShowtimeSeat]:
        stmt = select(ShowtimeSeat).where(
            ShowtimeSeat.showtime_id == showtime_id,
            ShowtimeSeat.id.in_(showtime_seat_ids)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def hold_seats(self, showtime_id: uuid.UUID, showtime_seat_ids: List[uuid.UUID], hold_expires_at: datetime) -> bool:
        seats = await self.get_seats_by_ids(showtime_id, showtime_seat_ids)
        
        if len(seats) != len(showtime_seat_ids):
            return False
            
        for seat in seats:
            if seat.status != SeatStatus.AVAILABLE:
                return False
                
            seat.status = SeatStatus.HOLDING
            seat.hold_expires_at = hold_expires_at
            
        try:
            await self.session.flush()
            return True
        except StaleDataError:
            return False
            
    async def update_seats_status(self, showtime_id: uuid.UUID, showtime_seat_ids: List[uuid.UUID], new_status: SeatStatus) -> bool:
        seats = await self.get_seats_by_ids(showtime_id, showtime_seat_ids)
        for seat in seats:
            seat.status = new_status
            if new_status == SeatStatus.BOOKED:
                seat.hold_expires_at = None
        try:
            await self.session.flush()
            return True
        except StaleDataError:
            return False
