from typing import List, Union

from fastapi import APIRouter, Request
from fastapi.exceptions import HTTPException
from sqlmodel import Session, or_, select

from ..db import ActiveSession
from ..models.content import Content, ContentIncoming, ContentResponse
from ..models.security import User
from ..security import AuthenticatedUser, get_current_user

router = APIRouter()


# MARK: 内容列表
"""
获取所有内容列表
- 返回所有内容项目
- 不需要认证
"""
@router.get("/", response_model=List[ContentResponse])
async def list_contents(*, session: Session = ActiveSession):
    contents = session.exec(select(Content)).all()
    return contents


# MARK: 查询单个内容
"""
查询单个内容
- 可以通过ID或slug查询
- 返回内容详情
- 如果内容不存在，返回404错误
"""
@router.get("/{id_or_slug}/", response_model=ContentResponse)
async def query_content(
    *, id_or_slug: Union[str, int], session: Session = ActiveSession
):
    content = session.query(Content).where(
        or_(
            Content.id == id_or_slug,
            Content.slug == id_or_slug,
        )
    )
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content.first()


# MARK: 创建新内容
"""
CREATE_CONTENT
- 需要已认证用户权限
- 自动关联当前用户ID
- 保存内容到数据库
- 返回创建的内容详情
"""
@router.post(
    "/", response_model=ContentResponse, dependencies=[AuthenticatedUser]
)
async def create_content(
    *,
    session: Session = ActiveSession,
    request: Request,
    content: ContentIncoming,
):
    # set the ownsership of the content to the current user
    db_content = Content.from_orm(content)
    user: User = get_current_user(request=request)
    db_content.user_id = user.id
    session.add(db_content)
    session.commit()
    session.refresh(db_content)
    return db_content


# MARK: 更新内容
"""
UPDATE_CONTENT
- 需要已认证用户权限
- 验证内容是否存在
- 验证当前用户是否有权限更新内容（拥有者或管理员）
- 更新内容并保存到数据库
- 返回更新后的内容详情
"""
@router.patch(
    "/{content_id}/",
    response_model=ContentResponse,
    dependencies=[AuthenticatedUser],
)
async def update_content(
    *,
    content_id: int,
    session: Session = ActiveSession,
    request: Request,
    patch: ContentIncoming,
):
    # Query the content
    content = session.get(Content, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Check the user owns the content
    current_user: User = get_current_user(request=request)
    if content.user_id != current_user.id and not current_user.superuser:
        raise HTTPException(
            status_code=403, detail="You don't own this content"
        )

    # Update the content
    patch_data = patch.dict(exclude_unset=True)
    for key, value in patch_data.items():
        setattr(content, key, value)

    # Commit the session
    session.commit()
    session.refresh(content)
    return content


# MARK: 删除内容
"""
DELETE_CONTENT
- 需要已认证用户权限
- 验证内容是否存在
- 验证当前用户是否有权限删除内容（拥有者或管理员）
- 删除内容并保存更改
- 返回操作结果
"""
@router.delete("/{content_id}/", dependencies=[AuthenticatedUser])
def delete_content(
    *, session: Session = ActiveSession, request: Request, content_id: int
):

    content = session.get(Content, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    # Check the user owns the content
    current_user = get_current_user(request=request)
    if content.user_id != current_user.id and not current_user.superuser:
        raise HTTPException(
            status_code=403, detail="You don't own this content"
        )
    session.delete(content)
    session.commit()
    return {"ok": True}
