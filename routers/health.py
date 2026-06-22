from fastapi import APIRouter

from database import database


router = APIRouter()


@router.get("/")
async def health():
    await database.ping()
    return {"status": "ok", "db": "connected"}
