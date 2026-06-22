from bson import ObjectId


class NoteRepository:
    """Database operations for notes owned by a single authenticated user."""

    def __init__(self, db):
        self.collection = db.notes

    async def list_for_user(self, user_email: str):
        notes = await self.collection.find({"user_email": user_email}).to_list(100)
        for note in notes:
            note["_id"] = str(note["_id"])
        return notes

    async def create(self, name: str, content: str, user_email: str):
        document = {"name": name, "content": content, "user_email": user_email}
        return await self.collection.insert_one(document)

    async def update(self, note_id: str, name: str, content: str, user_email: str):
        return await self.collection.update_one(
            {"_id": ObjectId(note_id), "user_email": user_email},
            {"$set": {"name": name, "content": content}},
        )

    async def delete(self, note_id: str, user_email: str):
        return await self.collection.delete_one(
            {"_id": ObjectId(note_id), "user_email": user_email}
        )
