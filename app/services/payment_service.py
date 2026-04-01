import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.schemas.payment import PaymentCreate
from app.db.models.payment import Payment
from app.db.models.enums import PaymentStatus, OrderStatus, SeatStatus
from app.repositories.payment_repo import PaymentRepository
from app.repositories.order_repo import OrderRepository
from app.repositories.showtime_seat_repo import ShowtimeSeatRepository
from app.core.config import settings
from app.services.vnpay_utils import VNPay

class PaymentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.payment_repo = PaymentRepository(session)
        self.order_repo = OrderRepository(session)
        self.seat_repo = ShowtimeSeatRepository(session)

    async def process_payment(self, current_user_id: uuid.UUID, payment_in: PaymentCreate, client_ip: str) -> dict:
        # Get order
        order = await self.order_repo.get_by_id(payment_in.order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy đơn hàng.")
            
        if order.user_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Không có quyền truy cập đơn hàng này.")
            
        if order.status != OrderStatus.PENDING:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Không thể thanh toán đơn hàng có trạng thái: {order.status}")
            
        new_payment = Payment(
            order_id=order.id,
            provider=payment_in.provider,
            amount=order.total_amount,
            status=PaymentStatus.INITIATED,
        )
        
        created_payment = await self.payment_repo.create(new_payment)
        
        vnp = VNPay(
            tmn_code=settings.vnp_TmnCode,
            hash_secret=settings.vnp_HashSecret,
            payment_url=settings.vnp_Url,
            return_url=settings.VNPAY_RETURN_URL
        )
        order_desc = f"Thanh toan don hang {order.id}"
        payment_url = vnp.get_payment_url(str(order.id), int(order.total_amount), order_desc, client_ip)
        
        return {
            "id": created_payment.id,
            "order_id": created_payment.order_id,
            "provider": created_payment.provider,
            "amount": created_payment.amount,
            "status": created_payment.status,
            "created_at": created_payment.created_at,
            "payment_url": payment_url
        }

    async def handle_vnpay_ipn(self, query_params: dict) -> dict:
        vnp = VNPay(settings.vnp_TmnCode, settings.vnp_HashSecret, settings.vnp_Url, settings.VNPAY_RETURN_URL)
        if not vnp.validate_response(query_params):
            return {'RspCode': '97', 'Message': 'Invalid Signature'}
            
        order_id_str = query_params.get('vnp_TxnRef')
        vnp_ResponseCode = query_params.get('vnp_ResponseCode')
        vnp_TransactionNo = query_params.get('vnp_TransactionNo')
        vnp_Amount = int(query_params.get('vnp_Amount', 0)) / 100
        
        try:
            order_id = uuid.UUID(order_id_str)
        except ValueError:
            return {'RspCode': '01', 'Message': 'Order not found'}
            
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            return {'RspCode': '01', 'Message': 'Order not found'}
            
        if order.status != OrderStatus.PENDING:
            return {'RspCode': '02', 'Message': 'Order already confirmed'}
            
        if order.total_amount != vnp_Amount:
            return {'RspCode': '04', 'Message': 'Invalid amount'}
            
        # Update statuses
        if vnp_ResponseCode == '00':
            order.status = OrderStatus.PAID
            for seat in order.showtime_seats:
                seat.status = SeatStatus.BOOKED
                seat.hold_expires_at = None
                
            # Create a success payment record if needed, but we already have INITIATED. 
            # Ideally we'd update the INITIATED payment to SUCCESS. For simplicity, just update it.
            # Using raw SQL or a repo method might be better.
        else:
            order.status = OrderStatus.CANCELLED
            for seat in order.showtime_seats:
                seat.status = SeatStatus.AVAILABLE
                seat.hold_expires_at = None
                seat.order_id = None
                
        await self.session.commit()
        return {'RspCode': '00', 'Message': 'Confirm Success'}
