from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class VenueBase(BaseModel):
    name: str = Field(..., max_length=255)
    address: str = Field(..., max_length=500)
    capacity: int = Field(..., gt=0)

class VenueCreate(VenueBase):
    """Schema for creating a Venue"""
    pass

class VenueUpdate(BaseModel):
    """Schema for updating a Venue"""
    name: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = Field(None, max_length=500)
    capacity: Optional[int] = Field(None, gt=0)

class VenueResponse(VenueBase):
    """Schema for Venue response"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
