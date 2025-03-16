from fastapi import APIRouter

# NOTE: 在这里可以配置显示在v1版本API文档中Content部分的路由
router = APIRouter()

# MARK: 获取内容列表
@router.get("/")
async def list_content():
    return {"message": "List content endpoint"} 


# MARK: 创建内容
@router.post("/")
async def ContentCreate():
    return {"message": "Create content endpoint"}


# MARK: 更新内容
@router.put("/{content_id}")
async def ContentUpdate(content_id: int):
    return {"message": "Update content endpoint"}


# MARK: 删除内容
@router.delete("/{content_id}")
async def delete_content(content_id: int):
    return {"message": "Delete content endpoint"}


# MARK: 获取内容详情
@router.get("/{content_id}")
async def get_content(content_id: int):
    return {"message": "Get content endpoint"}

# MARK: 搜索内容
@router.get("/search")
async def search_content(query: str):
    return {"message": "Search content endpoint"}


