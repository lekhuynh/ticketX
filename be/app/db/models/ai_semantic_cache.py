import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, text, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.db.base import Base

class AISemanticCache(Base):
    """
    Model lưu trữ kết quả Cache ngữ nghĩa (Semantic Cache) của các câu hỏi AI.
    Tên bảng: ai_semantic_cache
    """
    __tablename__ = "ai_semantic_cache"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )

    # Lọc ngữ cảnh theo tenant / user
    tenant_id: Mapped[str] = mapped_column(String(50), default="T-999", nullable=False)

    # Chứa nội dung câu hỏi
    query_text: Mapped[str] = mapped_column(String, nullable=False)

    # Vector embedding của câu hỏi - Chiều dài 768 (e5-base)
    embedding: Mapped[list[float]] = mapped_column(
        Vector(768), nullable=False
    )

    # Nội dung hoàn chỉnh do LLM trả về
    response: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    last_accessed: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "idx_ai_semantic_cache_embedding",
            embedding,
            postgresql_using="ivfflat",
            postgresql_ops={"embedding": "vector_cosine_ops"}
        ),
        UniqueConstraint("tenant_id", "query_text", name="uq_tenant_query")
    )
