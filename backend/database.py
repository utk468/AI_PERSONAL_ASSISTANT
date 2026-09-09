import sys
from typing import List, Optional
# pyrefly: ignore [missing-import]
from motor.motor_asyncio import AsyncIOMotorClient

from backend.config import settings
from backend.mongo_schema import ReminderDB

client: Optional[AsyncIOMotorClient] = None
collection = None
use_fallback = False


async def connect():
    global client, collection
    client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=2000)
    collection = client[settings.MONGODB_DB_NAME]["reminders"]


async def save_reminder(reminder: ReminderDB) -> bool:
    await collection.replace_one({"id": reminder.id}, reminder.model_dump(), upsert=True)
    return True


async def get_reminders(active_only: bool = False) -> List[ReminderDB]:
    query = {"status": "active"} if active_only else {}
    results = []
    async for doc in collection.find(query):
        doc.pop("_id", None)
        results.append(ReminderDB(**doc))
    return results


async def get_reminder(reminder_id: str) -> Optional[ReminderDB]:
    doc = await collection.find_one({"id": reminder_id})
    if doc:
        doc.pop("_id", None)
        return ReminderDB(**doc)
    return None


async def delete_reminder(reminder_id: str) -> bool:
    res = await collection.delete_one({"id": reminder_id})
    return res.deleted_count > 0


async def update_reminder_status(reminder_id: str, status: str, next_run_time: Optional[str] = None) -> bool:
    update_doc = {"$set": {"status": status}}
    if next_run_time:
        update_doc["$set"]["next_run_time"] = next_run_time
    res = await collection.update_one({"id": reminder_id}, update_doc)
    return res.modified_count > 0


db_manager = sys.modules[__name__]
