import uuid
from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.repositories.user_repo import UserRepository
from app.schemas.auth import UserCreate
from app.db.models.user import User
from app.db.models.refresh_token import RefreshToken
from app.core.security import hash_password, verify_password
class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def register_user(self, user_data: UserCreate) -> User:
        """Logic nghiệp vụ đăng ký người dùng mới."""
        
        # 1. Kiểm tra email đã tồn tại hay chưa
        existing_user = await self.user_repo.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # 2. Tạo User Model và hash password
        new_user = User(
            id=uuid.uuid4(),
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name
        )
        
        # 3. Gọi repository lưu user (flush)
        user = await self.user_repo.create_user(new_user)
        
        # 4. Commit toàn bộ thay đổi
        await self.session.commit()
        return user

    async def login_user(self, email: str, password: str) -> User | None:
        """Logic nghiệp vụ đăng nhập."""
        user = await self.user_repo.get_user_by_email(email)
        
        if not user:
            return Nonez
            
        if not verify_password(password, user.hashed_password):
            return None
            
        return user

    async def create_token_for_user(self, user: User) -> "TokenResponse":
        """Tạo JWT access token và refresh token cho user, lưu refresh token vào DB."""
        from app.core.security import create_access_token, create_refresh_token
        from app.core.config import settings
        from app.schemas.auth import TokenResponse
        
        access_token = create_access_token(
            data={"sub": str(user.id)}
        )
        refresh_token_str = create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        # Lưu Refresh Token vào Database
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        db_refresh_token = RefreshToken(
            id=uuid.uuid4(),
            user_id=user.id,
            token=refresh_token_str,
            expires_at=expires_at,
            revoked=False
        )
        await self.user_repo.create_refresh_token(db_refresh_token)
        await self.session.commit()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    async def refresh_token(self, old_refresh_token: str) -> tuple[str, str]:
        """Verify the old refresh token, generate new pairs, update DB."""
        from app.core.security import decode_token, create_access_token, create_refresh_token
        from app.core.config import settings
        
        # 1. Tìm token trong DB
        db_token = await self.user_repo.get_refresh_token(old_refresh_token)
        if not db_token or db_token.revoked or db_token.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token is invalid or expired"
            )
            
        # 2. Decode JWT payload
        payload = decode_token(old_refresh_token)
        user_id = payload.get("sub")
        token_type = payload.get("type")
        
        if user_id is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
            
        try:
            user_uuid = UUID(str(user_id))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user id"
            )
            
        # 3. Thu hồi (revoke) token cũ
        await self.user_repo.revoke_refresh_token(old_refresh_token)
        
        # 4. Sinh bộ token mới
        access_token = create_access_token({"sub": str(user_uuid)})
        new_refresh_token_str = create_refresh_token({"sub": str(user_uuid)})
        
        # 5. Lưu token mới vào DB
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        new_db_token = RefreshToken(
            id=uuid.uuid4(),
            user_id=user_uuid,
            token=new_refresh_token_str,
            expires_at=expires_at,
            revoked=False
        )
        await self.user_repo.create_refresh_token(new_db_token)
        await self.session.commit()
        
        return access_token, new_refresh_token_str

    async def logout_user(self, refresh_token: str) -> None:
        """Thu hồi refresh token khi logout."""
        db_token = await self.user_repo.get_refresh_token(refresh_token)
        if db_token:
            await self.user_repo.revoke_refresh_token(refresh_token)
            await self.session.commit()