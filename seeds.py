"""
Seed global starter templates into MongoDB.
Run once after first boot:  python -m backend.seeds
"""
import asyncio
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from utils.helpers import get_current_timestamp
from templates_data import GLOBAL_TEMPLATES


async def seed_templates():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB_NAME]

    existing = await db.mail_templates.count_documents({"is_global": True})
    if existing > 0:
        print(f"⚠️  {existing} global templates already exist — skipping. Delete them first to re-seed.")
        client.close()
        return

    now = get_current_timestamp()
    docs = []
    for t in GLOBAL_TEMPLATES:
        docs.append({
            "_id": str(uuid.uuid4()),
            "is_global": True,
            "user_id": "global",
            "name": t["name"],
            "subject": t["subject"],
            "html_body": t["html_body"].strip(),
            "created_at": now,
            "updated_at": now,
        })

    await db.mail_templates.insert_many(docs)
    print(f"✅  Seeded {len(docs)} global templates.")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_templates())
