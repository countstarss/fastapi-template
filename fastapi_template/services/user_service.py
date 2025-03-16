import logging
from typing import Optional, Union

from fastapi import HTTPException, status
from sqlmodel import Session, select, or_

from fastapi_template.models.security import User, UserCreate, UserResponse
from fastapi_template.security import get_password_hash
from fastapi_template.utils.pagination import PaginatedResponse, paginate

logger = logging.getLogger(__name__)

# MARK: 用户服务
"""
用户服务
- 封装用户相关的业务逻辑
- 提供用户的CRUD操作
- 提供用户查询和分页功能
"""
class UserService:
    def __init__(self, session: Session):
        self.session = session
      
    # MARK: getUserById 
    # 通过ID获取用户
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        通过ID获取用户
        
        参数:
            user_id: 用户ID
            
        返回:
            Optional[User]: 用户对象，如果不存在则返回None
        """
        return self.session.get(User, user_id)
        
    # MARK: getUserByUsername
    # 通过用户名获取用户
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        通过用户名获取用户
        
        参数:
            username: 用户名
            
        返回:
            Optional[User]: 用户对象，如果不存在则返回None
        """
        return self.session.exec(
            select(User).where(User.username == username)
        ).first()
        
    # MARK: getUser 
    # 通过ID或用户名获取用户
    def get_user(self, user_id_or_username: Union[int, str]) -> Optional[User]:
        """
        获取用户
        
        参数:
            user_id_or_username: 用户ID或用户名
            
        返回:
            Optional[User]: 用户对象，如果不存在则返回None
        """
        return self.session.exec(
            select(User).where(
                or_(
                    User.id == user_id_or_username,
                    User.username == user_id_or_username
                )
            )
        ).first()
        
    def list_users(
        self, 
        page: int = 1, 
        size: int = 10,
        username_filter: Optional[str] = None,
        superuser_filter: Optional[bool] = None,
        disabled_filter: Optional[bool] = None
    ) -> PaginatedResponse[UserResponse]:
        """
        获取用户列表
        
        参数:
            page: 页码
            size: 每页大小
            username_filter: 用户名过滤
            superuser_filter: 超级用户过滤
            disabled_filter: 禁用状态过滤
            
        返回:
            PaginatedResponse[UserResponse]: 分页用户列表
        """
        query = select(User)
        
        # MARK: 应用过滤器
        if username_filter:
            query = query.where(User.username.contains(username_filter))
            
        if superuser_filter is not None:
            query = query.where(User.superuser == superuser_filter)
            
        if disabled_filter is not None:
            query = query.where(User.disabled == disabled_filter)
            
        # MARK: 应用分页
        return paginate(self.session, query, page, size)
        



    # MARK: createUser
    # 创建用户
    def create_user(self, user_create: UserCreate) -> User:
        """
        创建用户
        
        参数:
            user_create: 用户创建数据
            
        返回:
            User: 创建的用户对象
            
        异常:
            HTTPException: 如果用户名已存在
        """
        # NOTE: 检查用户名是否已存在
        existing_user = self.get_user_by_username(user_create.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )
            
        # NOTE: 创建用户
        db_user = User(
            username=user_create.username,
            password=user_create.password,  # HashedPassword类型会自动处理哈希
            superuser=user_create.superuser,
            disabled=user_create.disabled
        )
        
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        
        return db_user
        


    # MARK: updateUser
    # 更新用户
    def update_user(
        self, 
        user_id: int, 
        username: Optional[str] = None,
        superuser: Optional[bool] = None,
        disabled: Optional[bool] = None
    ) -> User:
        """
        更新用户
        
        参数:
            user_id: 用户ID
            username: 新用户名
            superuser: 新超级用户状态
            disabled: 新禁用状态
            
        返回:
            User: 更新后的用户对象
            
        异常:
            HTTPException: 如果用户不存在或用户名已存在
        """
        # NOTE: 获取用户
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        # NOTE: 更新用户名
        if username and username != user.username:
            existing_user = self.get_user_by_username(username)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username already exists"
                )
                
            user.username = username
            
        # NOTE: 更新其他字段
        if superuser is not None:
            user.superuser = superuser
            
        if disabled is not None:
            user.disabled = disabled
            
        self.session.commit()
        self.session.refresh(user)
        
        return user
        

    # MARK: updatePassword
    # 更新用户密码
    def update_password(self, user_id: int, password: str) -> User:
        """
        更新用户密码
        
        参数:
            user_id: 用户ID
            password: 新密码
            
        返回:
            User: 更新后的用户对象
            
        异常:
            HTTPException: 如果用户不存在
        """
        # NOTE: 获取用户
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        # NOTE: 更新密码
        user.password = get_password_hash(password)
        
        self.session.commit()
        self.session.refresh(user)
        
        return user
        


    # MARK: deleteUser
    # 删除用户
    def delete_user(self, user_id: int) -> bool:
        """
        删除用户
        
        参数:
            user_id: 用户ID
            
        返回:
            bool: 是否成功删除
            
        异常:
            HTTPException: 如果用户不存在
        """
        # NOTE: 获取用户
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        # NOTE: 删除用户
        self.session.delete(user)
        self.session.commit()
        
        return True 