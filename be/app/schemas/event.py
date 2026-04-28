from pydantic import Field, BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.schemas.venue import VenueResponse

class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class ShowtimeMini(BaseModel):
    id: UUID
    start_time: datetime

    class Config:
        from_attributes = True

class EventResponse(EventBase):
    id: UUID
    venue_id: UUID
    is_active: bool
    created_at: datetime
    venue: Optional[VenueResponse] = None
    showtimes: List[ShowtimeMini] = []
    
    class Config:
        from_attributes = True