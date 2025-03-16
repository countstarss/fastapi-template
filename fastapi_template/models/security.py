from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

from fastapi_template.models.content import Content, ContentResponse


# MARK: 令牌模型
"""
令牌模型
- 用于API认证的令牌结构
- 包含访问令牌、刷新令牌和令牌类型
"""
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


# MARK: 刷新令牌模型
"""
刷新令牌模型
- 用于刷新访问令牌
- 仅包含刷新令牌字段
"""
class RefreshToken(BaseModel):
    refresh_token: str


# MARK: 令牌数据模型
"""
令牌数据模型
- 用于JWT令牌的负载数据
- 包含用户名信息
"""
class TokenData(BaseModel):
    username: Optional[str] = None


# MARK: 哈希密码类型
"""
哈希密码类型
- 自定义字符串类型，用于自动哈希密码
- 提供验证器以在保存前自动哈希明文密码
"""
class HashedPassword(str):
    """Takes a plain text password and hashes it.

    use this as a field in your SQLModel

    class User(SQLModel, table=True):
        username: str
        password: HashedPassword

    """

    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def validate(cls, v):
        """Accepts a plain text password and returns a hashed password."""
        if not isinstance(v, str):
            raise TypeError("string required")

        from fastapi_template.security import get_password_hash
        hashed_password = get_password_hash(v)
        # you could also return a string here which would mean model.password
        # would be a string, pydantic won't care but you could end up with some
        # confusion since the value's type won't match the type annotation
        # exactly
        return cls(hashed_password)


# MARK: 用户数据模型
"""
用户数据模型
- 定义用户表结构
- 包含用户名、密码、超级用户标志和禁用状态
- 与内容模型建立关联关系
"""
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(sa_column_kwargs={"unique": True})
    password: HashedPassword
    superuser: bool = False
    disabled: bool = False

    # it populates the .user attribute on the Content Model
    contents: List["Content"] = Relationship(back_populates="user")


# MARK: 用户响应模型
"""
用户响应模型
- 用于API响应的序列化
- 不包含密码字段，保证安全性
- 包含用户ID、用户名、状态和关联内容
"""
class UserResponse(BaseModel):
    """This is the User model to be used as a response_model
    it doesn't include the password.
    """

    id: int
    username: str
    disabled: bool
    superuser: bool
    contents: Optional[List[ContentResponse]] = Field(default_factory=list)


# MARK: 用户创建模型
"""
用户创建模型
- 用于创建新用户的数据验证
- 包含用户名、密码和可选的状态字段
"""
class UserCreate(BaseModel):
    """This is the User model to be used when creating a new user."""

    username: str
    password: str
    superuser: bool = False
    disabled: bool = False


# MARK: 用户密码修改模型
"""
用户密码修改模型
- 用于修改用户密码的数据验证
- 包含密码和确认密码字段
- 用于确保两次输入的密码一致
"""
class UserPasswordPatch(SQLModel):
    """This is to accept password for changing"""

    password: str
    password_confirm: str 