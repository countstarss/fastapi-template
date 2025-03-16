# fastapi_template/schemas/user.py
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

# MARK: 用户基础模型
class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    disabled: Optional[bool] = False
    superuser: Optional[bool] = False

# MARK: 创建用户请求模型
class UserCreate(UserBase):
    password: str
    password_confirm: str

    class Config:
        schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "password": "secret123",
                "password_confirm": "secret123",
                "disabled": False,
                "superuser": False
            }
        }

# MARK: 更新用户请求模型
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    disabled: Optional[bool] = None
    superuser: Optional[bool] = None

    class Config:
        schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "disabled": False,
                "superuser": False
            }
        }

# MARK: 用户响应模型
class UserResponse(UserBase):
    id: int
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "username": "johndoe",
                "email": "john@example.com",
                "disabled": False,
                "superuser": False
            }
        }