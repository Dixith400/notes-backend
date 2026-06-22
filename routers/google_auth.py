from fastapi import APIRouter
from starlette.requests import Request

from services.google_oauth_service import google_oauth_service


router = APIRouter()


@router.get("/auth/google")
async def google_login(request: Request):
    return await google_oauth_service.start_login(request)


@router.get("/auth/google/callback")
async def google_callback(request: Request):
    return await google_oauth_service.finish_login(request)
