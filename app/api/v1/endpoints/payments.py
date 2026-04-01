from typing import List
from app.core.rbac import require_admin
from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services.payment_service import PaymentService
from app.core.security import get_current_active_user
from app.db.models.user import User

router = APIRouter()

@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def process_payment(
    request: Request,
    payment_in: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Tạo URL thanh toán VNPAY
    """
    payment_service = PaymentService(db)
    client_ip = request.client.host if request.client else "127.0.0.1"
    
    return await payment_service.process_payment(current_user.id, payment_in, client_ip)

@router.get("/vnpay-ipn")
async def vnpay_ipn(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Webhook / IPN từ VNPAY gọi về Server
    """
    payment_service = PaymentService(db)
    query_params = dict(request.query_params)
    result = await payment_service.handle_vnpay_ipn(query_params)
    return JSONResponse(content=result)

@router.get("/vnpay-return")
async def vnpay_return(
    request: Request
):
    """
    User return url
    """
    # In a real app we might validate here again or just redirect to frontend
    query_params = request.query_params
    vnp_ResponseCode = query_params.get('vnp_ResponseCode')
    
    # URL Frontend (e.g., React App)
    # The actual VNPAY_RETURN_URL in .env points to frontend, but if it points here:
    frontend_url = "http://localhost:5173/payment/result"
    
    if vnp_ResponseCode == "00":
        return RedirectResponse(url=f"{frontend_url}?status=success")
    else:
        return RedirectResponse(url=f"{frontend_url}?status=failed")
@router.get("/", response_model=list[PaymentResponse])
async def list_payments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Return all payments (admin only)."""
    payment_service = PaymentService(db)
    return await payment_service.list_payments()
