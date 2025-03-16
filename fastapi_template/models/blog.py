from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

# MARK: 博客基础模型
"""
博客文章基础模型
- 定义文章的基本字段
- 包含标题、内容和发布状态
"""
class PostBase(SQLModel):
    title: str = Field(index=True)
    content: str
    published: bool = Field(default=True)

# MARK: 博客文章模型
"""
博客文章数据模型
- 继承自PostBase
- 添加ID、创建时间、更新时间和用户ID
- 建立与评论和点赞的关联关系
- 提供评论数、点赞数和热度分数计算属性
"""
class Post(PostBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="user.id")
    
    # Relationships
    comments: List["Comment"] = Relationship(back_populates="post")
    likes: List["Like"] = Relationship(back_populates="post")
    
    @property
    def comment_count(self) -> int:
        return len(self.comments)
    
    @property
    def like_count(self) -> int:
        return len(self.likes)
    
    @property
    def heat_score(self) -> float:
        # 简单的热度计算公式：点赞数 * 0.7 + 评论数 * 0.3
        return self.like_count * 0.7 + self.comment_count * 0.3

# MARK: 评论基础模型
"""
评论基础模型
- 定义评论的基本字段
- 仅包含评论内容
"""
class CommentBase(SQLModel):
    content: str
    
# MARK: 评论数据模型
"""
评论数据模型
- 继承自CommentBase
- 添加ID、创建时间、更新时间和用户ID
- 建立与文章的关联关系
- 支持评论嵌套（根评论和父评论）
"""
class Comment(CommentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="user.id")
    post_id: int = Field(foreign_key="post.id")
    root_id: Optional[int] = Field(default=None, foreign_key="comment.id")  # 根评论ID
    parent_id: Optional[int] = Field(default=None, foreign_key="comment.id")  # 父评论ID
    
    # Relationships
    post: Post = Relationship(back_populates="comments")
    
    # 明确指定外键关系，解决AmbiguousForeignKeysError
    replies: List["Comment"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "Comment.id==Comment.parent_id",
            "remote_side": "Comment.parent_id",
            "foreign_keys": "[Comment.parent_id]",
            "cascade": "all, delete-orphan"
        }
    )
    
# MARK: 点赞数据模型
"""
点赞数据模型
- 记录用户对文章的点赞
- 包含用户ID和文章ID
- 建立与文章的关联关系
"""
class Like(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="user.id")
    post_id: int = Field(foreign_key="post.id")
    
    # Relationships
    post: Post = Relationship(back_populates="likes")

# MARK: 评论响应模型
"""
评论响应模型
- 用于API响应的序列化
- 包含评论ID、创建时间和用户ID
- 支持嵌套回复列表
"""
class CommentResponse(CommentBase):
    id: int
    created_at: datetime
    user_id: int
    replies: List["CommentResponse"] = []
    
# MARK: 文章响应模型
"""
文章响应模型
- 用于API响应的序列化
- 继承自PostBase
- 添加ID、创建时间、更新时间和用户ID
- 包含评论数、点赞数和热度分数
"""
class PostResponse(PostBase):
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int
    comment_count: int
    like_count: int
    heat_score: float 