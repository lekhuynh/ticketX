# app/db/models/showtime_seat.py

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    ForeignKey,
    DateTime,
    Numeric,
    Enum as SQLEnum,
    UniqueConstraint,
    Index,
    Integer,
    CheckConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from .enums import SeatStatus


class ShowtimeSeat(Base):
    __tablename__ = "showtime_seats"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    showtime_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("showtimes.id", ondelete="CASCADE"),
        nullable=False,
    )

    seat_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("seats.id", ondelete="CASCADE"),
        nullable=False,
    )

    order_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("orders.id", ondelete="SET NULL"),
    )

    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    status: Mapped[SeatStatus] = mapped_column(
        SQLEnum(SeatStatus, native_enum=False, length=20),
        default=SeatStatus.AVAILABLE,
        nullable=False,
    )

    hold_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        server_default="1",
        nullable=False,
    )

    showtime: Mapped["Showtime"] = relationship(back_populates="seats")
    order: Mapped[Optional["Order"]] = relationship(back_populates="showtime_seats")
    seat: Mapped["Seat"] = relationship(back_populates="showtime_seats")

    __table_args__ = (
        UniqueConstraint("showtime_id", "seat_id", name="uq_showtime_seat"),
        Index("idx_showtime_status", "showtime_id", "status"),
        Index("idx_showtime_order", "order_id"),
        CheckConstraint("price >= 0", name="ck_showtime_seat_price_positive"),
    )

    __mapper_args__ = {"version_id_col": version}