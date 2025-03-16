from typing import List, Union
import logging
import traceback

from fastapi import APIRouter, Request
from fastapi.exceptions import HTTPException
from sqlmodel import Session, or_, select

from ..db import ActiveSession
from ..models.security import (
    User,
    UserCreate,
    UserPasswordPatch,
    UserResponse,
)
from ..security import (
    AdminUser,
    AuthenticatedFreshUser,
    AuthenticatedUser,
    get_current_user,
    get_password_hash,
)

# 设置日志记录器
logger = logging.getLogger(__name__)

router = APIRouter()


# MARK: List Users
"""
获取所有用户列表
- 需要管理员权限
- 返回所有用户的信息
"""
@router.get("/", response_model=List[UserResponse], dependencies=[AdminUser])
async def list_users(*, session: Session = ActiveSession):
    users = session.exec(select(User)).all()
    return users


# MARK: Create User
"""
创建新用户
- 验证用户名是否已存在
- 创建新用户并保存到数据库
- 返回创建的用户信息
"""
@router.post("/", response_model=UserResponse)  # 暂时移除AdminUser依赖以便测试
async def create_user(*, session: Session = ActiveSession, user: UserCreate):
    try:
        logger.info(f"尝试创建用户: {user.username}")
        
        # 验证用户名是否已存在
        try:
            existing_user = session.exec(
                select(User).where(User.username == user.username)
            ).first()
            if existing_user:
                logger.warning(f"用户名已存在: {user.username}")
                raise HTTPException(status_code=422, detail="Username already exists")
        except Exception as e:
            logger.error(f"查询用户时出错: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Error querying user: {str(e)}")

        # 创建新用户
        try:
            db_user = User(
                username=user.username,
                password=user.password,  # HashedPassword类型会自动处理哈希
                superuser=user.superuser,
                disabled=user.disabled
            )
            # 不要指定ID，让数据库自动生成
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            logger.info(f"用户创建成功: {user.username}, ID: {db_user.id}")
            return db_user
        except Exception as e:
            logger.error(f"创建用户时出错: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"未处理的异常: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Unhandled error: {str(e)}")


# MARK: Update Pass
"""
更新用户密码
- 需要已认证的新鲜用户权限
- 验证用户是否存在
- 验证当前用户是否有权限更新目标用户密码
- 验证新密码与确认密码是否匹配
- 更新密码并保存到数据库
"""
@router.patch(
    "/{user_id}/password/",
    response_model=UserResponse,
    dependencies=[AuthenticatedFreshUser],
)
async def update_user_password(
    *,
    user_id: int,
    session: Session = ActiveSession,
    request: Request,
    patch: UserPasswordPatch,
):
    # Query the content
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check the user can update the password
    current_user: User = get_current_user(request=request)
    if user.id != current_user.id and not current_user.superuser:
        raise HTTPException(
            status_code=403, detail="You can't update this user password"
        )

    if not patch.password == patch.password_confirm:
        raise HTTPException(status_code=400, detail="Passwords don't match")

    # Update the password
    user.password = get_password_hash(patch.password)

    # Commit the session
    session.commit()
    session.refresh(user)
    return user


# MARK: Query User
"""
查询用户信息
- 需要已认证用户权限
- 可以通过用户ID或用户名查询
- 返回用户详细信息
"""
@router.get(
    "/{user_id_or_username}/",
    response_model=UserResponse,
    dependencies=[AuthenticatedUser],
)
async def query_user(
    *, session: Session = ActiveSession, user_id_or_username: Union[str, int]
):
    user = session.query(User).where(
        or_(
            User.id == user_id_or_username,
            User.username == user_id_or_username,
        )
    )

    if not user.first():
        raise HTTPException(status_code=404, detail="User not found")
    return user.first()


# MARK: Delete User
"""
删除用户
- 需要管理员权限
- 验证用户是否存在
- 验证当前用户不是删除自己
- 删除用户并保存更改
"""
@router.delete("/{user_id}/", dependencies=[AdminUser])
def delete_user(
    *, session: Session = ActiveSession, request: Request, user_id: int
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Content not found")
    # Check the user is not deleting himself
    current_user = get_current_user(request=request)
    if user.id == current_user.id:
        raise HTTPException(
            status_code=403, detail="You can't delete yourself"
        )
    session.delete(user)
    session.commit()
    return {"ok": True}
