from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_profile():
    return {"message": "Get profile endpoint"} 