# app/db/models/event.py

import uuid
from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, String, Boolean, DateTime, Index, text, UniqueConstraint, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    venue_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("venues.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    venue: Mapped["Venue"] = relationship(back_populates="events")

    showtimes: Mapped[List["Showtime"]] = relationship(
        back_populates="event",
        cascade="all, delete-orphan",
    )
    ai_docs: Mapped[list["AIDoc"]] = relationship("AIDoc", back_populates="event")

    __table_args__ = (
        Index("idx_event_venue", "venue_id"),
        UniqueConstraint("venue_id", "name", name="uq_venue_event_name"),
    )