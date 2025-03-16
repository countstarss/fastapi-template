from fastapi import APIRouter

router = APIRouter()

@router.post("/token")
async def login_for_access_token():
    return {"message": "Login endpoint"} 