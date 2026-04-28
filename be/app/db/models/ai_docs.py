import uuid
from datetime import datetime
from typing import Optional, Any

from sqlalchemy import (
    ForeignKey, DateTime, Index, text,
    Boolean, Integer, String
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base
# Lưu ý: Nếu bạn dùng pgvector bản mới nhất, có thể dùng VECTOR (viết hoa)
from pgvector.sqlalchemy import Vector 


class AIDoc(Base):
    """
    Model lưu trữ các tài liệu, nội dung phục vụ cho AI (RAG, Search).
    Tên bảng: ai_docs
    """
    __tablename__ = "ai_docs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # Link với event thật - Khi xóa event sẽ tự động xóa các docs liên quan
    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Nội dung tài liệu AI (description, chính sách, FAQ, hoặc các chunk nhỏ)
    content: Mapped[str] = mapped_column(nullable=False)

    # Vector embedding - Chiều dài 768 phù hợp với model e5-base
    embedding: Mapped[list[float]] = mapped_column(
        Vector(768)
    )

    # TSV precomputed for fast Hybrid Search
    from sqlalchemy.dialects.postgresql import TSVECTOR
    tsv: Mapped[Optional[Any]] = mapped_column(TSVECTOR, nullable=True)

    # Tenant-Aware Multi-Tenant ID isolation (SaaS requirement)
    tenant_id: Mapped[str] = mapped_column(
        String(50), 
        default="T-999", 
        nullable=False,
        server_default="T-999" # Default for backwards compatibility
    )

    # --- Các trường quản lý nội dung ---
    type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True,
        comment="Loại nội dung: description, policy, faq, terms, ..."
    )

    metadata_info: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True,
        name="metadata", # Giữ nguyên tên cột trong DB là metadata nếu muốn
        comment="Thông tin bổ sung: nguồn, độ dài, chunk_index, ..."
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False,
        comment="Trạng thái kích hoạt"
    )

    chunk_order: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True,
        comment="Thứ tự chunk nếu nội dung gốc được chia nhỏ"
    )

    language: Mapped[Optional[str]] = mapped_column(
        String(10), nullable=True,
        comment="Mã ngôn ngữ (vi, en, ...)"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # --- Relationship ---
    # Cần đảm bảo bên model Event cũng có thuộc tính: 
    # ai_docs: Mapped[list["AIDoc"]] = relationship(back_populates="event")
    event: Mapped["Event"] = relationship(back_populates="ai_docs")

    __table_args__ = (
    Index("idx_ai_docs_event", "event_id"),
    Index("idx_ai_docs_type", "type"),

    # filter nhanh
    Index("idx_ai_docs_event_active", "event_id", "is_active"),

    # full-text search
    Index(
        "idx_ai_docs_content_tsv",
        text("to_tsvector('simple', content)"),
        postgresql_using="gin"
    ),

    # metadata search
    Index(
        "idx_ai_docs_metadata",
        "metadata",
        postgresql_using="gin"
    ),

    # vector index (NOTE: chỉnh bằng SQL ngoài)
    Index(
        "idx_ai_docs_embedding",
        embedding,
        postgresql_using="ivfflat",
        postgresql_ops={"embedding": "vector_cosine_ops"}
    ),

    # chống duplicate
    Index(
        "uniq_event_chunk",
        "event_id",
        "chunk_order",
        unique=True
    ),
)