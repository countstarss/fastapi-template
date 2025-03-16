from fastapi import APIRouter

router = APIRouter()

# NOTE: 在这里可以配置显示在v1版本API文档中Auth部分的路由


@router.post("/token")
async def login_for_access_token():
    return {"message": "Login endpoint"} 

# MARK: 刷新令牌
@router.post("/refresh-token")
async def refresh_token():
    return {"message": "Refresh token endpoint"}


# MARK: 注销
@router.post("/logout")
async def logout():
    return {"message": "Logout endpoint"}


# MARK: 注册
@router.post("/register")
async def register():
    return {"message": "Register endpoint"}


# MARK: 验证令牌
@router.post("/verify-token")
async def verify_token():
    return {"message": "Verify token endpoint"}


