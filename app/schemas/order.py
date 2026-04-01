from typing import List, Optional
import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, condecimal

from app.db.models.enums import OrderStatus, SeatStatus

class OrderCreate(BaseModel):
    showtime_id: uuid.UUID
    showtime_seat_ids: List[uuid.UUID] = Field(..., min_items=1, description="List of showtime seat IDs to book")

class ShowtimeSeatResponse(BaseModel):
    id: uuid.UUID
    seat_id: uuid.UUID
    price: condecimal(ge=Decimal("0.00"), decimal_places=2) # type: ignore
    status: SeatStatus
    hold_expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    total_amount: condecimal(ge=Decimal("0.00"), decimal_places=2) # type: ignore
    status: OrderStatus
    expires_at: datetime
    created_at: datetime
    showtime_seats: List[ShowtimeSeatResponse] = []

    class Config:
        from_attributes = True
