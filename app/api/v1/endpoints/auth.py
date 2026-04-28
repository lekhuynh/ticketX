from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from app.core.security import (
    authenticate_user,
    create_access_token,
    hash_password,
    get_current_user
)
from app.core.config import settings
from app.db.session import get_db
from app.schemas.auth import UserCreate, TokenResponse, UserResponse, RefreshTokenRequest
from app.db.models.user import User
import uuid

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    from app.services.auth_service import AuthService
    
    # Khởi tạo Service
    auth_service = AuthService(db)
    
    # Delegate logic đăng ký cho service
    new_user = await auth_service.register_user(user_data)
    return new_user

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login user and return access token."""
    from app.services.auth_service import AuthService
    
    auth_service = AuthService(db)
    
    # Authenticate user qua Service
    user = await auth_service.login_user(
        email=form_data.username,  # OAuth2 form uses 'username' field for email
        password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return await auth_service.create_token_for_user(user)

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    """Get current user info."""
    return current_user


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token."""
    from app.services.auth_service import AuthService
    
    auth_service = AuthService(db)
    
    # Refresh token qua Service
    access_token, new_refresh_token = await auth_service.refresh_token(request.refresh_token)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/logout", response_model=TokenResponse)
async def logout(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Logout user."""
    from app.services.auth_service import AuthService
    
    auth_service = AuthService(db)
    
    # Logout user bằng cách thu hồi token qua Service
    await auth_service.logout_user(request.refresh_token)
    
    return TokenResponse(
        access_token="",
        refresh_token="",
        token_type="bearer",
        expires_in=0
    )