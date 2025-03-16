from fastapi_template.api.v1.endpoints import auth, users, content, profile

# MARK: 导出所有端点
# NOTE: 这些是显示在v1版本API文档中的端点

__all__ = ["auth", "users", "content", "profile"]
