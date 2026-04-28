from typing import List
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.venue import VenueCreate, VenueUpdate, VenueResponse
from app.services.venue_service import VenueService
from app.core.rbac import require_admin
from app.db.models.user import User

router = APIRouter()

@router.post("/", response_model=VenueResponse, status_code=status.HTTP_201_CREATED)
async def create_venue(
    venue_in: VenueCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)  # Chỉ có ADMIN mới được tạo địa điểm
):
    """
    Tạo địa điểm mới (Chỉ dành cho ADMIN)
    """
    venue_service = VenueService(db)
    return await venue_service.create_venue(venue_in)

@router.get("/", response_model=List[VenueResponse])
async def read_venues(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy danh sách địa điểm (Ai cũng xem được)
    """
    venue_service = VenueService(db)
    return await venue_service.get_venues(skip=skip, limit=limit)

@router.get("/{venue_id}", response_model=VenueResponse)
async def read_venue(
    venue_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy thông tin chi tiết một địa điểm (Ai cũng xem được)
    """
    venue_service = VenueService(db)
    return await venue_service.get_venue(venue_id)

@router.put("/{venue_id}", response_model=VenueResponse)
async def update_venue(
    venue_id: uuid.UUID,
    venue_in: VenueUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)  # Chỉ có ADMIN mới được cập nhật địa điểm
):
    """
    Cập nhật thông tin địa điểm (Chỉ dành cho ADMIN)
    """
    venue_service = VenueService(db)
    return await venue_service.update_venue(venue_id, venue_in)

@router.delete("/{venue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_venue(
    venue_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)  # Chỉ có ADMIN mới được xoá địa điểm
):
    """
    Xoá địa điểm (Chỉ dành cho ADMIN)
    """
    venue_service = VenueService(db)
    await venue_service.delete_venue(venue_id)
