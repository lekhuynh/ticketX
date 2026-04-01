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

router.get()
