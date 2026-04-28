from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from app.db.models.enums import SeatStatus
from .seat import SeatResponse

class ShowtimeSeatBase(BaseModel):
    showtime_id: UUID
    seat_id: UUID
    price: Decimal
    status: SeatStatus

class ShowtimeSeatCreate(ShowtimeSeatBase):
    pass

class ShowtimeSeatResponse(ShowtimeSeatBase):
    id: UUID
    order_id: Optional[UUID] = None
    seat: Optional[SeatResponse] = None

    class Config:
        from_attributes = True
