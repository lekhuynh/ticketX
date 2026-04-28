import uuid
from typing import List, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.schemas.order import OrderCreate
from app.db.models.order import Order
from app.db.models.enums import OrderStatus
from app.repositories.order_repo import OrderRepository
from app.repositories.showtime_seat_repo import ShowtimeSeatRepository

HOLD_MINUTES = 15

class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.order_repo = OrderRepository(session)
        self.seat_repo = ShowtimeSeatRepository(session)

    async def create_order(self, current_user_id: uuid.UUID, order_in: OrderCreate) -> Order:
        seats = await self.seat_repo.get_seats_by_ids(order_in.showtime_id, order_in.showtime_seat_ids)
        if len(seats) != len(order_in.showtime_seat_ids):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Một số ghế không tồn tại hoặc không thuộc suất diễn này.")
            
        total_amount = sum(seat.price for seat in seats)
        hold_expires_at = datetime.now(timezone.utc) + timedelta(minutes=HOLD_MINUTES)
        
        # Try to hold seats
        success = await self.seat_repo.hold_seats(order_in.showtime_id, order_in.showtime_seat_ids, hold_expires_at)
        if not success:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ghế đã được đặt hoặc đang được giữ bởi người khác.")

        # Create Order
        new_order = Order(
            user_id=current_user_id,
            total_amount=total_amount,
            status=OrderStatus.PENDING,
            expires_at=hold_expires_at
        )
        
        # Liên kết ghế với order
        for seat in seats:
            seat.order = new_order
            
        created_order = await self.order_repo.create(new_order)
        return created_order

    async def get_order(self, current_user_id: uuid.UUID, order_id: uuid.UUID) -> Order:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy đơn hàng.")
        if order.user_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Không có quyền truy cập đơn hàng này.")
        return order
