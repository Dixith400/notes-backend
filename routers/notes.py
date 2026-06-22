from fastapi import APIRouter, Depends

from database import database
from models import NotePayload
from repositories.note_repository import NoteRepository
from services.auth_service import get_current_user


router = APIRouter()
notes_repository = NoteRepository(database.db)


@router.get("/notes")
async def get_notes(current_user: str = Depends(get_current_user)):
    return await notes_repository.list_for_user(current_user)


@router.post("/notes")
async def create_notes(note: NotePayload, current_user: str = Depends(get_current_user)):
    await notes_repository.create(note.name, note.content, current_user)
    return {"message": "notes created"}


@router.put("/notes/{note_id}")
async def update_notes(
    note_id: str,
    note: NotePayload,
    current_user: str = Depends(get_current_user),
):
    await notes_repository.update(note_id, note.name, note.content, current_user)
    return {"message": "notes updated successfully"}


@router.delete("/notes/{note_id}")
async def delete_notes(note_id: str, current_user: str = Depends(get_current_user)):
    await notes_repository.delete(note_id, current_user)
    return {"message": "notes deleted successfully"}
