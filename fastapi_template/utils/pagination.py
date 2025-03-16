from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel
from sqlmodel import Session, SQLModel, select

T = TypeVar('T')

# MARK: 分页响应模型
"""
分页响应模型
- 包含分页数据和元数据
- 支持泛型，可以适用于任何数据类型
"""
class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool


# MARK: 分页查询
"""
分页查询函数
- 对SQLModel查询结果进行分页
- 返回分页响应对象
"""
def paginate(
    session: Session, 
    query, 
    page: int = 1, 
    size: int = 10
) -> PaginatedResponse:
    """
    对查询结果进行分页
    
    参数:
        session: 数据库会话
        query: SQLModel查询对象
        page: 页码，从1开始
        size: 每页大小
        
    返回:
        PaginatedResponse: 分页响应对象
    """
    # 确保页码和大小有效
    if page < 1:
        page = 1
    if size < 1:
        size = 10
        
    # 计算总数
    total = session.exec(select(query.original._raw_columns[0].count())).one()
    
    # 计算总页数
    pages = (total + size - 1) // size
    
    # 应用分页
    items = session.exec(
        query.offset((page - 1) * size).limit(size)
    ).all()
    
    # 构建响应
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )


# MARK: 简单分页
"""
简单分页函数
- 对普通列表进行分页
- 返回分页响应对象
"""
def paginate_list(
    items: List[T], 
    page: int = 1, 
    size: int = 10
) -> PaginatedResponse[T]:
    """
    对列表进行分页
    
    参数:
        items: 要分页的列表
        page: 页码，从1开始
        size: 每页大小
        
    返回:
        PaginatedResponse: 分页响应对象
    """
    # 确保页码和大小有效
    if page < 1:
        page = 1
    if size < 1:
        size = 10
        
    # 计算总数
    total = len(items)
    
    # 计算总页数
    pages = (total + size - 1) // size
    
    # 应用分页
    start = (page - 1) * size
    end = start + size
    paged_items = items[start:end]
    
    # 构建响应
    return PaginatedResponse(
        items=paged_items,
        total=total,
        page=page,
        size=size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    ) 