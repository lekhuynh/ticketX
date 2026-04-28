from typing import List
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.seat import SeatCreate, SeatUpdate, SeatResponse
from app.services.seat_service import SeatService
from app.core.rbac import require_admin
from app.db.models.user import User

router = APIRouter()

@router.post("/venues/{venue_id}/seats", response_model=SeatResponse, status_code=status.HTTP_201_CREATED)
async def create_seat_for_venue(
    venue_id: uuid.UUID,
    seat_in: SeatCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)  # Chỉ có ADMIN mới được tạo ghế
):
    """
    Tạo ghế mới cho một Venue cụ thể (Chỉ dành cho ADMIN)
    """
    seat_service = SeatService(db)
    return await seat_service.create_seat(venue_id, seat_in)

@router.get("/venues/{venue_id}/seats", response_model=List[SeatResponse])
async def read_seats_by_venue(
    venue_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy danh sách ghế của một địa điểm (Ai cũng xem được)
    """
    seat_service = SeatService(db)
    return await seat_service.get_seats_by_venue(venue_id, skip=skip, limit=limit)

@router.get("/seats/{seat_id}", response_model=SeatResponse)
async def read_seat(
    seat_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy thông tin chi tiết một ghế chuyên biệt (Ai cũng xem được)
    """
    seat_service = SeatService(db)
    return await seat_service.get_seat(seat_id)

@router.put("/seats/{seat_id}", response_model=SeatResponse)
async def update_seat(
    seat_id: uuid.UUID,
    seat_in: SeatUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)  # Chỉ có ADMIN mới được cập nhật
):
    """
    Cập nhật thông tin ghế (Chỉ dành cho ADMIN)
    """
    seat_service = SeatService(db)
    return await seat_service.update_seat(seat_id, seat_in)

@router.delete("/seats/{seat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seat(
    seat_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)  # Chỉ có ADMIN mới được xoá
):
    """
    Xoá ghế (Chỉ dành cho ADMIN)
    """
    seat_service = SeatService(db)
    await seat_service.delete_seat(seat_id)
