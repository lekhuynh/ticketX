from pydantic import BaseModel, Field, model_validator
from typing import Optional
from uuid import UUID
from datetime import datetime

class ShowtimeBase(BaseModel):
    start_time: datetime
    end_time: datetime

class ShowtimeCreate(ShowtimeBase):
    """Schema for creating a Showtime"""
    event_id: UUID

    @model_validator(mode='after')
    def validate_times(self) -> 'ShowtimeCreate':
        if self.end_time <= self.start_time:
            raise ValueError('end_time must be after start_time')
        return self

class ShowtimeUpdate(BaseModel):
    """Schema for updating a Showtime"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @model_validator(mode='after')
    def validate_times(self) -> 'ShowtimeUpdate':
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValueError('end_time must be after start_time')
        return self

class ShowtimeResponse(ShowtimeBase):
    """Schema for Showtime response"""
    id: UUID
    event_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

