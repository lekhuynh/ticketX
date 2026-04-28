from typing import List
from fastapi import HTTPException, status, Depends
from app.db.models.user import User
from app.db.models.enums import Role
from app.core.security import get_current_active_user
import logging

logger = logging.getLogger(__name__)

class RoleCheck:
    def __init__(self, allowed_roles: List[Role]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_active_user)):
        
        # ADMIN luôn có quyền
        if current_user.role == Role.ADMIN:
            return current_user

        if current_user.role not in self.allowed_roles:
            logger.warning(f"User {current_user.id} with role {current_user.role} attempted to access restricted route.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn chả có quyền méo gì vào đây cả ^-^"
            )
        return current_user


require_admin = RoleCheck([Role.ADMIN])
require_organizer = RoleCheck([Role.ORGANIZER])