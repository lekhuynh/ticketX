# app/db/models/seat.py
import uuid
from datetime import datetime
from typing import List

from sqlalchemy import (
    ForeignKey,
    String,
    Integer,
    DateTime,
    UniqueConstraint,
    Index,
    CheckConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Seat(Base):
    __tablename__ = "seats"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    venue_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("venues.id", ondelete="CASCADE"),
        nullable=False,
    )

    row_label: Mapped[str] = mapped_column(String(10), nullable=False)
    seat_number: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    venue: Mapped["Venue"] = relationship(back_populates="seats")

    showtime_seats: Mapped[List["ShowtimeSeat"]] = relationship(
        back_populates="seat",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("venue_id", "row_label", "seat_number", name="uq_seat_position"),
        Index("idx_seat_venue_row", "venue_id", "row_label"),
        CheckConstraint("seat_number > 0", name="ck_seat_number_positive"),
    )