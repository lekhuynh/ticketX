import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, condecimal

from app.db.models.enums import PaymentStatus

class PaymentCreate(BaseModel):
    order_id: uuid.UUID
    provider: str

class PaymentResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    provider: str
    provider_transaction_id: str | None = None
    amount: condecimal(ge=Decimal("0.00"), decimal_places=2) # type: ignore
    status: PaymentStatus
    created_at: datetime
    payment_url: str | None = None

    class Config:
        from_attributes = True
