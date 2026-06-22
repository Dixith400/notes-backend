from motor.motor_asyncio import AsyncIOMotorClient

from config import settings


class MongoDatabase:
    """Owns the Mongo client so data access stays outside route functions."""

    def __init__(self, mongo_url: str, database_name: str):
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[database_name]

    async def ping(self):
        return await self.db.command("ping")


database = MongoDatabase(settings.mongo_url, "notesdb")
