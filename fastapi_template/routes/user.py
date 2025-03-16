from typing import List, Optional, Union
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlmodel import Session

from ..db import ActiveSession
from ..hooks.use_auth import use_auth, UseAuth
from ..models.security import User, UserCreate, UserPasswordPatch, UserResponse
from ..services.user_service import UserService
from ..utils.pagination import PaginatedResponse

# 设置日志记录器
logger = logging.getLogger(__name__)

router = APIRouter()


# MARK: List Users
"""
获取所有用户列表
- 需要管理员权限
- 支持分页和过滤
- 返回所有用户的信息
"""
@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页大小"),
    username: Optional[str] = Query(None, description="用户名过滤"),
    superuser: Optional[bool] = Query(None, description="超级用户过滤"),
    disabled: Optional[bool] = Query(None, description="禁用状态过滤"),
    session: Session = ActiveSession,
    auth: UseAuth = Depends(use_auth)
):
    # 验证权限
    auth.require_permission(request, admin_required=True)
    
    # 使用用户服务获取用户列表
    user_service = UserService(session)
    return user_service.list_users(
        page=page,
        size=size,
        username_filter=username,
        superuser_filter=superuser,
        disabled_filter=disabled
    )


# MARK: Create User
"""
创建新用户
- 验证用户名是否已存在
- 创建新用户并保存到数据库
- 返回创建的用户信息
"""
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request,
    user: UserCreate,
    session: Session = ActiveSession,
    auth: UseAuth = Depends(use_auth)
):
    # 验证权限（只有管理员可以创建用户）
    auth.require_permission(request, admin_required=True)
    
    # 使用用户服务创建用户
    user_service = UserService(session)
    try:
        return user_service.create_user(user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建用户时出错: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )


# MARK: Update Pass
"""
更新用户密码
- 需要已认证的用户权限
- 验证用户是否存在
- 验证当前用户是否有权限更新目标用户密码
- 验证新密码与确认密码是否匹配
- 更新密码并保存到数据库
"""
@router.patch("/{user_id}/password/", response_model=UserResponse)
async def update_user_password(
    user_id: int,
    patch: UserPasswordPatch,
    request: Request,
    session: Session = ActiveSession,
    auth: UseAuth = Depends(use_auth)
):
    # 验证权限（用户只能更新自己的密码，管理员可以更新任何用户的密码）
    current_user = auth.get_active_user(request)
    
    # 检查密码是否匹配
    if patch.password != patch.password_confirm:
        raise HTTPException(status_code=400, detail="Passwords don't match")
    
    # 使用用户服务获取用户
    user_service = UserService(session)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 检查权限
    if user.id != current_user.id and not current_user.superuser:
        raise HTTPException(
            status_code=403, detail="You can't update this user password"
        )
    
    # 更新密码
    return user_service.update_password(user_id, patch.password)


# MARK: Query User
"""
查询用户信息
- 需要已认证用户权限
- 可以通过用户ID或用户名查询
- 返回用户详细信息
"""
@router.get("/{user_id_or_username}/", response_model=UserResponse)
async def query_user(
    user_id_or_username: Union[str, int],
    request: Request,
    session: Session = ActiveSession,
    auth: UseAuth = Depends(use_auth)
):
    # 验证权限
    auth.get_active_user(request)
    
    # 使用用户服务获取用户
    user_service = UserService(session)
    user = user_service.get_user(user_id_or_username)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


# MARK: Delete User
"""
删除用户
- 需要管理员权限
- 验证用户是否存在
- 验证当前用户不是删除自己
- 删除用户并保存更改
"""
@router.delete("/{user_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    request: Request,
    session: Session = ActiveSession,
    auth: UseAuth = Depends(use_auth)
):
    # 验证权限
    current_user = auth.require_permission(request, admin_required=True)
    
    # 检查用户是否存在
    user_service = UserService(session)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 检查用户是否删除自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=403, detail="You can't delete yourself"
        )
    
    # 删除用户
    user_service.delete_user(user_id)
    
    return None
