import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.order import OrderCreate, OrderResponse
from app.services.order_service import OrderService
from app.core.security import get_current_active_user
from app.db.models.user import User

router = APIRouter()

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Tạo đơn hàng mới (Giữ ghế)
    """
    order_service = OrderService(db)
    return await order_service.create_order(current_user.id, order_in)

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_details(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lấy chi tiết đơn hàng
    """
    order_service = OrderService(db)
    return await order_service.get_order(current_user.id, order_id)
