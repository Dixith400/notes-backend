from fastapi import APIRouter

from models import UserCredentials
from services.auth_service import auth_service, get_current_user
from fastapi import Depends


router = APIRouter()


@router.post("/register")
async def register(user: UserCredentials):
    return await auth_service.register(user.email, user.password)


@router.post("/login")
async def login(user: UserCredentials):
    return await auth_service.login(user.email, user.password)


@router.get("/test")
async def test_auth(current_user: str = Depends(get_current_user)):
    return {"logged in as": current_user}
