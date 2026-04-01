# app/db/models/venue.py
import uuid
from datetime import datetime
from typing import List

from sqlalchemy import String, Integer, DateTime, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Venue(Base):
    __tablename__ = "venues"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    seats: Mapped[List["Seat"]] = relationship(
        back_populates="venue",
        cascade="all, delete-orphan",
    )

    events: Mapped[List["Event"]] = relationship(
        back_populates="venue",
        cascade="all, delete-orphan",
    )

    __table_args__ = (Index("idx_venue_name", "name"),)