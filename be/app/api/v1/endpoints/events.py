from fastapi import HTTPException, APIRouter, Depends, status
from typing import List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models.event import Event
from app.schemas.event import EventCreate, EventResponse, EventUpdate
from app.services.event_service import EventService
from app.core.rbac import require_admin, require_organizer
from app.db.models.user import User


router = APIRouter()

@router.post("/venues/{venue_id}/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    venue_id: uuid.UUID,
    event_in: EventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """Tạo địa điểm mới (Chỉ dành cho Organizer) """
    event = EventService(db)
    return await event.create_event(venue_id, event_in)

@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    event = EventService(db)
    return await event.get_event(event_id)

@router.put("/events/{event_id}", response_model=EventResponse)
async def put_event(
    event_id: uuid.UUID,
    event_in: EventUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    event = EventService(db)
    return await event.update_event(event_id, event_in)

@router.delete("/events/{event_id}")
async def del_event(
    event_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    event = EventService(db)
    await event.delete_event(event_id)
    return None

@router.get("/events", response_model=List[EventResponse])
async def get_all_event(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    event = EventService(db)
    return await event.get_all_event(skip=skip, limit= limit)