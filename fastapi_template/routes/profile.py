from fastapi import APIRouter

from ..models.security import User, UserResponse
from ..security import AuthenticatedUser

router = APIRouter()


# MARK: MY_PROFILE
"""
获取当前用户的个人资料
- 需要已认证用户权限
- 返回当前登录用户的详细信息
"""
@router.get("/profile", response_model=UserResponse)
async def my_profile(current_user: User = AuthenticatedUser):
    return current_user
