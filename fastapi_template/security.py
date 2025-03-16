from datetime import datetime, timedelta
from typing import Callable, Optional, Union

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session

# 导入从models移动过来的模型
from fastapi_template.models.security import (
    Token, TokenData, User, UserResponse, HashedPassword
)

from .config import settings
from .db import engine

# MARK: 密码上下文
"""
密码上下文
- 使用bcrypt算法
- 自动弃用旧算法
"""
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = settings.security.secret_key
ALGORITHM = settings.security.algorithm


# MARK: 验证密码
"""
验证密码
- 使用密码上下文验证密码
- 返回验证结果
"""
def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# MARK: 获取密码哈希
"""
获取密码哈希
- 使用密码上下文获取密码哈希
- 返回哈希值
"""
def get_password_hash(password) -> str:
    return pwd_context.hash(password)


# MARK: 创建访问令牌
"""
创建访问令牌
- 使用JWT编码数据
- 设置过期时间
- 返回编码后的令牌
"""
def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "scope": "access_token"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# MARK: 创建刷新令牌
"""
创建刷新令牌
- 使用JWT编码数据
- 设置过期时间
- 返回编码后的令牌
"""
def create_refresh_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "scope": "refresh_token"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# MARK: 验证用户
"""
验证用户
- 使用用户查询函数获取用户
- 验证密码
- 返回验证结果
"""
def authenticate_user(
    get_user: Callable, username: str, password: str
) -> Union[User, bool]:
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


# MARK: 获取用户
"""
获取用户
- 使用数据库会话查询用户
- 返回查询结果
"""
def get_user(username) -> Optional[User]:
    with Session(engine) as session:
        return session.query(User).where(User.username == username).first()


# MARK: 获取当前用户
"""
获取当前用户
- 使用OAuth2密码授权获取用户
- 返回当前用户
"""
def get_current_user(
    token: str = Depends(oauth2_scheme), request: Request = None, fresh=False
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if request:
        if authorization := request.headers.get("authorization"):
            try:
                token = authorization.split(" ")[1]
            except IndexError:
                raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    if fresh and (not payload["fresh"] and not user.superuser):
        raise credentials_exception

    return user


# MARK: 获取当前活跃用户
"""
获取当前活跃用户
- 依赖于get_current_user
- 验证用户是否禁用
- 返回当前活跃用户
"""
async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


AuthenticatedUser = Depends(get_current_active_user)


# MARK: 获取当前新鲜用户
"""
获取当前新鲜用户
- 依赖于get_current_user
- 验证用户是否新鲜
- 返回当前新鲜用户
"""
def get_current_fresh_user(
    token: str = Depends(oauth2_scheme), request: Request = None
) -> User:
    return get_current_user(token, request, True)


AuthenticatedFreshUser = Depends(get_current_fresh_user)


# MARK: 获取当前管理员用户
"""
获取当前管理员用户
- 依赖于get_current_user
- 验证用户是否为管理员
- 返回当前管理员用户
"""
async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not an admin user"
        )
    return current_user


# MARK: 管理员用户依赖
"""
管理员用户依赖
- 依赖于get_current_admin_user
- 返回当前管理员用户
"""
AdminUser = Depends(get_current_admin_user)


# MARK: 验证令牌
"""
验证令牌
- 依赖于oauth2_scheme
- 获取当前用户
"""
async def validate_token(token: str = Depends(oauth2_scheme)) -> User:
    user = get_current_user(token=token)
    return user
