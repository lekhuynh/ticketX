from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, users, events, venues,
    seats, showtimes, orders, payments, audit_logs,lc_chat
)

# Tạo router cho v1
router = APIRouter()

# Include tất cả endpoints
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(events.router, tags=["Events"])
router.include_router(venues.router, prefix="/venues", tags=["Venues"])
router.include_router(seats.router, prefix="/seats", tags=["Seats"])
router.include_router(showtimes.router,  tags=["Showtimes"])
router.include_router(orders.router, prefix="/orders", tags=["Orders"])
router.include_router(payments.router, prefix="/payments", tags=["Payments"])
router.include_router(lc_chat.router, prefix="/lc-chat", tags=["LC Chat"])
# router.include_router(audit_logs.router, prefix="/audit-logs", tags=["Audit Logs"])