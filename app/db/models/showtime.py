# app/db/models/showtime.py

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, DateTime, UniqueConstraint, Index, text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Showtime(Base):
    __tablename__ = "showtimes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
    )

    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    event: Mapped["Event"] = relationship(back_populates="showtimes")

    seats: Mapped[List["ShowtimeSeat"]] = relationship(
        back_populates="showtime",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_showtime_start", "start_time"),
        UniqueConstraint("event_id", "start_time", name="uq_event_showtime_start"),
        CheckConstraint('end_time > start_time', name='ck_showtime_end_after_start'),
    )

 