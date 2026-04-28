import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

# pgvector
from pgvector.sqlalchemy import Vector


class EventAI(Base):
    __tablename__ = "event_ai"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # link với event thật
    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
    )

    # nội dung AI (policy, description, FAQ...)
    content: Mapped[str] = mapped_column(nullable=False)

    # vector embedding
    embedding: Mapped[list[float]] = mapped_column(
        Vector(1024)  # Groq/Llama thường ~1024 hoặc 768
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # relationship
    event: Mapped["Event"] = relationship(back_populates="ai_docs")

    __table_args__ = (
        Index("idx_event_ai_event", "event_id"),
    )