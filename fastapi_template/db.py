from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from .config import settings

# MARK: 创建数据库引擎
"""
创建数据库引擎
- 使用配置文件中的数据库URI
- 设置是否启用SQL日志（echo）
"""
engine = create_engine(
    settings.db.uri,
    echo=settings.db.echo,
)


# MARK: 创建数据库表
"""
创建数据库表
- 使用SQLModel的metadata对象
"""
def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine)


# MARK: 获取数据库会话
"""
获取数据库会话
- 使用SQLModel的Session类
- 在请求上下文管理器中创建会话
"""
def get_session():
    with Session(engine) as session:
        yield session


# MARK: 依赖注入
"""
依赖注入
- 使用get_session作为依赖注入的函数
"""
ActiveSession = Depends(get_session)
