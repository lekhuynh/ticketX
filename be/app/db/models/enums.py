import enum
class Role(str, enum.Enum):
    CUSTOMER = "CUSTOMER"
    ORGANIZER = "ORGANIZER"
    ADMIN = "ADMIN"

class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

class SeatStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    HOLDING = "HOLDING"
    BOOKED = "BOOKED"

class PaymentStatus(str, enum.Enum):
    INITIATED = "INITIATED"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"