from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class SeatBase(BaseModel):
    row_label: str = Field(..., max_length=10)
    seat_number: int = Field(..., gt=0)

class SeatCreate(SeatBase):
    """Schema for creating a Seat"""
    pass

class SeatUpdate(BaseModel):
    """Schema for updating a Seat"""
    row_label: Optional[str] = Field(None, max_length=10)
    seat_number: Optional[int] = Field(None, gt=0)

class SeatResponse(SeatBase):
    """Schema for Seat response"""
    id: UUID
    venue_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
