from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union

from pydantic import BaseModel, Extra
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from fastapi_template.models.security import User


# MARK: CONTENT_MODEL
"""
内容数据模型
- 定义内容表结构
- 包含标题、别名、正文、发布状态等字段
- 与用户模型建立关联关系
"""
class Content(SQLModel, table=True):
    """This is an example model for your application.

    Replace with the *things* you do in your application.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    slug: str = Field(default=None)
    text: str
    published: bool = False
    created_time: str = Field(
        default_factory=lambda: datetime.now().isoformat()
    )
    tags: str = Field(default="")
    user_id: Optional[int] = Field(foreign_key="user.id")

    # It populates a `.contents` attribute to the `User` model.
    user: Optional["User"] = Relationship(back_populates="contents")


# MARK: CONTENT_RESPONSE
"""
内容响应模型
- 用于API响应的序列化
- 处理标签从字符串到列表的转换
"""
class ContentResponse(BaseModel):
    """This the serializer exposed on the API"""

    id: int
    title: str
    slug: str
    text: str
    published: bool
    created_time: str
    tags: List[str]
    user_id: int

    def __init__(self, *args, **kwargs):
        # tags to model representation
        tags = kwargs.pop("tags", None)
        if tags and isinstance(tags, str):
            kwargs["tags"] = tags.split(",")
        super().__init__(*args, **kwargs)


# MARK: CONTENT_INCOMING
"""
内容输入模型
- 用于POST/PATCH请求的数据验证和处理
- 处理标签从列表到字符串的转换
- 自动生成别名(slug)
"""
class ContentIncoming(BaseModel):
    """This is the serializer used for POST/PATCH requests"""

    title: Optional[str]
    text: Optional[str]
    published: Optional[bool] = False
    tags: Optional[Union[List[str], str]]

    class Config:
        extra = Extra.allow
        arbitrary_types_allowed = True

    def __init__(self, *args, **kwargs):
        # tags to database representation
        tags = kwargs.pop("tags", None)
        if tags and isinstance(tags, list):
            kwargs["tags"] = ",".join(tags)
        super().__init__(*args, **kwargs)
        self.generate_slug()

    def generate_slug(self):
        """Generate a slug from the title."""
        if self.title:
            self.slug = self.title.lower().replace(" ", "-")
