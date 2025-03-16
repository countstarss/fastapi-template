# fastapi_template/api/deps.py
from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from fastapi_template.db import get_session
from fastapi_template.models.security import User
from fastapi_template.services.user_service import UserService
from fastapi_template.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# MARK: 数据库会话依赖
def get_db() -> Generator:
    db = get_session()
    try:
        yield db
    finally:
        db.close()

# MARK: 用户服务依赖
def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

# MARK: 当前用户依赖
def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
        
    user = user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
        
    return user

# MARK: 当前活跃用户依赖
def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# MARK: 管理员用户依赖
def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if not current_user.superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user