import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.order import Order
from app.db.models.enums import OrderStatus
from app.db.models.showtime_seat import ShowtimeSeat

class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create(self, order: Order) -> Order:
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        # Tải kèm showtime_seats
        stmt = select(Order).options(selectinload(Order.showtime_seats)).where(Order.id == order.id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_id(self, order_id: uuid.UUID) -> Optional[Order]:
        # ĐÃ SỬA: Thay 'id' bằng 'order_id' để khớp với tham số truyền vào
        stmt = select(Order).options(selectinload(Order.showtime_seats)).where(Order.id == order_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_status(self, order_id: uuid.UUID, status: OrderStatus) -> Optional[Order]:
        stmt = select(Order).where(Order.id == order_id)
        result = await self.session.execute(stmt)
        order = result.scalars().first()
        if order:
            order.status = status
            await self.session.commit()
            await self.session.refresh(order)
        return order