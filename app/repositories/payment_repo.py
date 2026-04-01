import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.payment import Payment
from app.db.models.enums import PaymentStatus

class PaymentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create(self, payment: Payment) -> Payment:
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return payment

    async def get_by_id(self, payment_id: uuid.UUID) -> Optional[Payment]:
        stmt = select(Payment).where(Payment.id == payment_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_status(self, payment_id: uuid.UUID, status: PaymentStatus) -> Optional[Payment]:
        stmt = select(Payment).where(Payment.id == payment_id)
        result = await self.session.execute(stmt)
        payment = result.scalars().first()
        if payment:
            payment.status = status
            await self.session.commit()
            await self.session.refresh(payment)
        return payment
