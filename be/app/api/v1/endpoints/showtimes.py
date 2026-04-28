from typing import List
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.showtime import ShowtimeCreate, ShowtimeUpdate, ShowtimeResponse
from app.schemas.showtime_seat import ShowtimeSeatResponse
from app.services.showtime_service import ShowtimeService
from app.services.seat_service import SeatService
from app.core.rbac import require_admin, require_organizer
from app.db.models.user import User

router = APIRouter()

@router.post("/events/{event_id}/showtimes", response_model=ShowtimeResponse, status_code=status.HTTP_201_CREATED)
async def create_showtime_for_event(
    event_id: uuid.UUID,
    showtime_in: ShowtimeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_organizer) # Organizer hoặc Admin uỷ quyền
):
    """
    Tạo suất diễn mới cho một sự kiện cụ thể
    """
    showtime_service = ShowtimeService(db)
    # Đảm bảo event_id trên URL và body là khớp
    showtime_in.event_id = event_id 
    return await showtime_service.create_showtime(showtime_in)

@router.get("/events/{event_id}/showtimes", response_model=List[ShowtimeResponse])
async def read_showtimes_by_event(
    event_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy danh sách các suất diễn của một sự kiện (Public)
    """
    showtime_service = ShowtimeService(db)
    return await showtime_service.get_showtimes_by_event(event_id, skip=skip, limit=limit)

@router.get("/showtimes/{showtime_id}", response_model=ShowtimeResponse)
async def read_showtime(
    showtime_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy chi tiết một suất diễn (Public)
    """
    showtime_service = ShowtimeService(db)
    return await showtime_service.get_showtime(showtime_id)

@router.get("/showtimes/{showtime_id}/seats", response_model=List[ShowtimeSeatResponse])
async def read_seats_by_showtime(
    showtime_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Lấy bản đồ ghế của một suất diễn (Đã kèm trạng thái trống/đã đặt)
    """
    # Ta dùng SeatService ở đây để tận dụng logic lấy theo showtime_id
    seat_service = SeatService(db)
    return await seat_service.get_seats_by_showtime(showtime_id)

@router.put("/showtimes/{showtime_id}", response_model=ShowtimeResponse)
async def update_showtime(
    showtime_id: uuid.UUID,
    showtime_in: ShowtimeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Cập nhật thời gian suất diễn
    """
    showtime_service = ShowtimeService(db)
    return await showtime_service.update_showtime(showtime_id, showtime_in)

@router.delete("/showtimes/{showtime_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_showtime(
    showtime_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_organizer)
):
    """
    Xoá một suất diễn
    """
    showtime_service = ShowtimeService(db)
    await showtime_service.delete_showtime(showtime_id)

