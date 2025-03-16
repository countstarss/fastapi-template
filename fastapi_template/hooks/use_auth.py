from typing import Callable, Optional, Tuple, Union
from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session

from fastapi_template.db import get_session
from fastapi_template.models.security import User
from fastapi_template.security import (
    get_current_user, get_current_active_user, get_current_admin_user
)

# MARK: 使用认证
"""
认证钩子
- 封装认证相关的逻辑
- 提供获取当前用户的函数
- 提供检查权限的函数
"""
class UseAuth:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session
        
    def get_current_user(self, request: Request) -> User:
        """
        获取当前用户
        
        参数:
            request: 请求对象
            
        返回:
            User: 当前用户
            
        异常:
            HTTPException: 如果用户未认证
        """
        return get_current_user(request=request)
        
    def get_active_user(self, request: Request) -> User:
        """
        获取当前活跃用户
        
        参数:
            request: 请求对象
            
        返回:
            User: 当前活跃用户
            
        异常:
            HTTPException: 如果用户未认证或已禁用
        """
        user = self.get_current_user(request)
        if user.disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return user
        
    def get_admin_user(self, request: Request) -> User:
        """
        获取当前管理员用户
        
        参数:
            request: 请求对象
            
        返回:
            User: 当前管理员用户
            
        异常:
            HTTPException: 如果用户未认证或不是管理员
        """
        user = self.get_active_user(request)
        if not user.superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Not an admin user"
            )
        return user
        
    def check_permission(
        self, 
        request: Request, 
        resource_id: Optional[int] = None,
        resource_owner_id: Optional[int] = None,
        admin_required: bool = False
    ) -> Tuple[bool, User]:
        """
        检查权限
        
        参数:
            request: 请求对象
            resource_id: 资源ID
            resource_owner_id: 资源所有者ID
            admin_required: 是否需要管理员权限
            
        返回:
            Tuple[bool, User]: (是否有权限, 当前用户)
        """
        try:
            if admin_required:
                user = self.get_admin_user(request)
                return True, user
                
            user = self.get_active_user(request)
            
            # 如果是管理员，总是有权限
            if user.superuser:
                return True, user
                
            # 如果没有指定资源ID或所有者ID，只检查用户是否活跃
            if resource_id is None and resource_owner_id is None:
                return True, user
                
            # 检查用户是否是资源所有者
            if resource_owner_id is not None:
                return user.id == resource_owner_id, user
                
            # 如果提供了资源ID，需要查询资源所有者
            # 这里需要根据实际情况实现
            # 例如：
            # resource = self.session.get(Resource, resource_id)
            # if resource and resource.user_id == user.id:
            #     return True, user
                
            return False, user
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error checking permission: {str(e)}"
            )
            
    def require_permission(
        self,
        request: Request,
        resource_id: Optional[int] = None,
        resource_owner_id: Optional[int] = None,
        admin_required: bool = False
    ) -> User:
        """
        要求权限
        
        参数:
            request: 请求对象
            resource_id: 资源ID
            resource_owner_id: 资源所有者ID
            admin_required: 是否需要管理员权限
            
        返回:
            User: 当前用户
            
        异常:
            HTTPException: 如果用户没有权限
        """
        has_permission, user = self.check_permission(
            request, resource_id, resource_owner_id, admin_required
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource"
            )
            
        return user


# 创建一个依赖项
def use_auth(session: Session = Depends(get_session)) -> UseAuth:
    return UseAuth(session=session) 