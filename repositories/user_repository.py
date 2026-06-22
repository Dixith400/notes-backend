class UserRepository:
    """Database operations for users."""

    def __init__(self, db):
        self.collection = db.user

    async def find_by_email(self, email: str):
        return await self.collection.find_one({"email": email})

    async def create(self, email: str, password):
        return await self.collection.insert_one({"email": email, "password": password})
