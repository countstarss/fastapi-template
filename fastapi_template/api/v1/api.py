# fastapi_template/api/v1/api.py
from fastapi import APIRouter

from fastapi_template.api.v1.endpoints import users, auth, content, profile

# MARK: 创建API路由
api_router = APIRouter()

# NOTE: 显示在v1版本API文档中的端点
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])