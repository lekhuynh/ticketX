from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User
from app.db.models.refresh_token import RefreshToken
import uuid


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        """Truy vấn user theo email"""
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def create_user(self, user: User) -> User:
        """Tạo user mới nhưng chưa commit transaction"""
        self.session.add(user)
        # flush đẩy thay đổi xuống DB để lấy ID tự tăng/UUID, nhưng chưa chốt (commit)
        await self.session.flush()
        return user

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        """Truy vấn user theo ID"""
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def update_user(self, user: User) -> User:
        """Cập nhật thông tin user nhưng chưa commit transaction"""
        # User đã được theo dõi bởi session, nên khi thay đổi thông số, chỉ cần flush
        await self.session.flush()
        return user

    async def delete_user(self, user: User) -> User:
        """Xóa user nhưng chưa commit transaction"""
        await self.session.delete(user)
        await self.session.flush()
        return user

    async def create_refresh_token(self, refresh_token: RefreshToken) -> RefreshToken:
        """Lưu refresh token vào database"""
        self.session.add(refresh_token)
        await self.session.flush()
        return refresh_token
        
    async def get_refresh_token(self, token: str) -> RefreshToken | None:
        """Tra cứu refresh token"""
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        return result.scalar_one_or_none()
        
    async def revoke_refresh_token(self, token: str) -> None:
        """Thu hồi (revoke) refresh token"""
        await self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.token == token)
            .values(revoked=True)
        )
        # Hoặc xoá luôn token: 
        # await self.session.execute(delete(RefreshToken).where(RefreshToken.token == token))