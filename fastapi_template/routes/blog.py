from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func, desc, asc
from ..db import get_session
from ..models.blog import Post, PostBase, Comment, CommentBase, Like, PostResponse, CommentResponse
# 注释掉认证导入，但保留代码以便之后恢复
# from ..security import get_current_user

router = APIRouter(prefix="/blog", tags=["blog"])

# MARK: CREATE_POST
"""
创建新博客文章
- 接收文章标题、内容和发布状态
- 自动关联当前用户ID（测试模式下使用固定ID=1）
- 返回创建的文章详情
"""
@router.post("/posts/", response_model=PostResponse)
def create_post(
    post: PostBase,
    session: Session = Depends(get_session),
    # 移除认证依赖，添加默认用户ID
    # current_user: dict = Depends(get_current_user)
):
    db_post = Post.from_orm(post)
    # 使用固定用户ID进行测试
    db_post.user_id = 1  # 假设ID为1的用户存在
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post

# MARK: GET_POSTS
"""
获取博客文章列表
- 支持分页（skip和limit参数）
- 支持按创建时间或热度排序
- 支持升序或降序排列
- 返回文章列表，包含评论数、点赞数和热度分数
"""
@router.get("/posts/", response_model=List[PostResponse])
def get_posts(
    skip: int = 0,
    limit: int = 10,
    sort_by: str = Query("created_at", regex="^(created_at|heat_score)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    session: Session = Depends(get_session)
):
    query = select(Post)
    
    # 排序逻辑
    if sort_by == "heat_score":
        # 对于热度排序，我们需要计算热度分数
        # 这里使用自定义SQL表达式来计算热度
        heat_score = (
            select([Post.id, 
                   (select(func.count()).select_from(Like).where(Like.post_id == Post.id).label('like_count') * 0.7 +
                    select(func.count()).select_from(Comment).where(Comment.post_id == Post.id).label('comment_count') * 0.3
                   ).label('heat_score')])
            .select_from(Post)
            .subquery()
        )
        query = query.join(heat_score, Post.id == heat_score.c.id)
        query = query.order_by(
            desc(heat_score.c.heat_score) if order == "desc" else asc(heat_score.c.heat_score)
        )
    else:
        # 创建时间排序
        query = query.order_by(
            desc(Post.created_at) if order == "desc" else asc(Post.created_at)
        )
    
    posts = session.exec(query.offset(skip).limit(limit)).all()
    return posts

# MARK: GET_POST
"""
获取单个博客文章详情
- 通过文章ID查询
- 返回文章详细信息，包含评论数、点赞数和热度分数
- 如果文章不存在，返回404错误
"""
@router.get("/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, session: Session = Depends(get_session)):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

# MARK: CREATE_COMMENT
"""
创建评论
- 可以对文章进行评论
- 支持嵌套评论（通过parent_id参数）
- 自动关联当前用户ID（测试模式下使用固定ID=1）
- 自动处理评论层级关系（root_id和parent_id）
- 返回创建的评论详情
"""
@router.post("/posts/{post_id}/comments/", response_model=CommentResponse)
def create_comment(
    post_id: int,
    comment: CommentBase,
    parent_id: Optional[int] = None,
    session: Session = Depends(get_session),
    # 移除认证依赖，添加默认用户ID
    # current_user: dict = Depends(get_current_user)
):
    # 验证帖子是否存在
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db_comment = Comment.from_orm(comment)
    db_comment.post_id = post_id
    # 使用固定用户ID进行测试
    db_comment.user_id = 1  # 假设ID为1的用户存在
    
    if parent_id:
        # 验证父评论是否存在
        parent_comment = session.get(Comment, parent_id)
        if not parent_comment:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        
        db_comment.parent_id = parent_id
        # 如果父评论有root_id，使用它的root_id，否则使用父评论的id作为root_id
        db_comment.root_id = parent_comment.root_id or parent_comment.id
    
    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    return db_comment

# MARK: GET_COMMENTS
"""
获取文章评论列表
- 通过文章ID查询
- 支持分页（skip和limit参数）
- 返回树形结构的评论列表（根评论及其所有子评论）
- 按创建时间降序排序
"""
@router.get("/posts/{post_id}/comments/", response_model=List[CommentResponse])
def get_comments(
    post_id: int,
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session)
):
    # 只获取根评论（没有parent_id的评论）
    query = select(Comment).where(
        Comment.post_id == post_id,
        Comment.parent_id == None
    ).order_by(Comment.created_at.desc())
    
    comments = session.exec(query.offset(skip).limit(limit)).all()
    
    # 递归获取所有回复
    def get_replies(comment_id: int) -> List[Comment]:
        replies_query = select(Comment).where(Comment.parent_id == comment_id)
        replies = session.exec(replies_query).all()
        for reply in replies:
            reply.replies = get_replies(reply.id)
        return replies
    
    # 为每个根评论获取回复
    for comment in comments:
        comment.replies = get_replies(comment.id)
    
    return comments

# MARK: LIKE_POST
"""
点赞/取消点赞文章
- 通过文章ID进行点赞操作
- 如果用户已经点赞，则取消点赞
- 如果用户未点赞，则添加点赞
- 自动关联当前用户ID（测试模式下使用固定ID=1）
- 返回操作结果消息
"""
@router.post("/posts/{post_id}/like")
def like_post(
    post_id: int,
    session: Session = Depends(get_session),
    # 移除认证依赖，添加默认用户ID
    # current_user: dict = Depends(get_current_user)
):
    # 检查帖子是否存在
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # 使用固定用户ID进行测试
    user_id = 1  # 假设ID为1的用户存在
    
    # 检查是否已经点赞
    existing_like = session.exec(
        select(Like).where(
            Like.post_id == post_id,
            Like.user_id == user_id
        )
    ).first()
    
    if existing_like:
        # 如果已经点赞，则取消点赞
        session.delete(existing_like)
        session.commit()
        return {"message": "Like removed"}
    
    # 创建新的点赞
    like = Like(post_id=post_id, user_id=user_id)
    session.add(like)
    session.commit()
    return {"message": "Post liked"} 