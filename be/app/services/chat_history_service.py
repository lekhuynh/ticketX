# app/services/chat_history_service.py
import uuid
from typing import List, Dict
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.chat_history import ChatHistory

class ChatHistoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_history(self, user_id: uuid.UUID, limit: int = 20) -> List[Dict[str, str]]:
        """
        Fetch recent chat history for a user, formatted for LangChain.
        """
        query = (
            select(ChatHistory)
            .where(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        messages = result.scalars().all()
        
        # Reverse to get chronological order
        return [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(messages)
        ]

    async def save_message(self, user_id: uuid.UUID, role: str, content: str):
        """
        Save a single message to history.
        """
        message = ChatHistory(
            user_id=user_id,
            role=role,
            content=content
        )
        self.db.add(message)
        await self.db.commit()

    async def clear_history(self, user_id: uuid.UUID):
        """
        Delete all chat history for a user.
        """
        query = delete(ChatHistory).where(ChatHistory.user_id == user_id)
        await self.db.execute(query)
        await self.db.commit()
