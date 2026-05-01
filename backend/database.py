import certifi
import bcrypt as _bcrypt
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from backend.config import settings
from datetime import datetime, timezone

client: AsyncIOMotorClient = None
DATABASE_NAME = settings.MONGODB_DB_NAME

async def connect_db():
    global client
    if client is None:
        try:
            # On Vercel, try with certifi first, fallback to standard if needed
            client = AsyncIOMotorClient(
                settings.MONGODB_URI, 
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=5000
            )
            # Ping to verify
            await client.admin.command('ping')
            print("MongoDB connected successfully.")
        except Exception as e:
            print(f"Primary MongoDB connection failed: {e}. Trying fallback...")
            client = AsyncIOMotorClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
            print("MongoDB connected with fallback.")

async def close_db():
    global client
    if client is not None:
        client.close()
        client = None
        print("MongoDB client closed.")

async def get_db() -> AsyncIOMotorDatabase:
    global client
    if client is None:
        await connect_db()
    return client[DATABASE_NAME]

async def init_db(db: AsyncIOMotorDatabase):
    # 1. users
    await db.users.create_index("email", unique=True)
    # 2. user_credentials (changed to allow multiple profiles)
    await db.user_credentials.create_index("user_id")
    await db.user_credentials.create_index([("user_id", 1), ("smtp_user", 1)], unique=True, sparse=True)
    # 3. mail_templates
    await db.mail_templates.create_index("user_id")
    # 4. contact_lists
    await db.contact_lists.create_index("user_id")
    # 5. mail_jobs
    await db.mail_jobs.create_index([("user_id", 1), ("status", 1)])
    # 6. mail_logs
    await db.mail_logs.create_index([("user_id", 1), ("job_id", 1), ("sent_at", 1)])
    # 7. audit_logs
    await db.audit_logs.create_index([("user_id", 1), ("timestamp", 1)])
    # 8. scheduled_tasks
    await db.scheduled_tasks.create_index([("user_id", 1), ("next_run", 1)])
    # 9. reply_inbox
    await db.reply_inbox.create_index([("user_id", 1), ("received_at", 1), ("is_read", 1)])
    # 10. revoked_tokens
    await db.revoked_tokens.create_index("jti", unique=True)
    await db.revoked_tokens.create_index("revoked_at", expireAfterSeconds=604800)  # 7 days TTL TTL index

    print("Database initialized with all 10 indexes.")

async def seed_admin(db: AsyncIOMotorDatabase):
    admin_email = settings.ADMIN_EMAIL
    admin_password = settings.ADMIN_PASSWORD
    admin_name = settings.ADMIN_NAME or "Admin"

    if not admin_email or not admin_password:
        print("ADMIN_EMAIL or ADMIN_PASSWORD not configured — skipping admin seed.")
        return

    hashed_password = _bcrypt.hashpw(admin_password.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")
    admin_exists = await db.users.find_one({"email": admin_email})

    if not admin_exists:
        import uuid
        admin_user = {
            "_id": str(uuid.uuid4()),
            "email": admin_email,
            "name": admin_name,
            "org_name": "Admin",
            "hashed_password": hashed_password,
            "role": "admin",
            "is_active": True,
            "created_at": datetime.now(timezone.utc)
        }
        await db.users.insert_one(admin_user)
        print(f"Admin user ({admin_email}) created.")
    else:
        # Always sync password + role from env so changing ADMIN_PASSWORD takes effect immediately
        await db.users.update_one(
            {"email": admin_email},
            {"$set": {
                "hashed_password": hashed_password,
                "role": "admin",
                "is_active": True,
                "name": admin_name,
            }}
        )
        print(f"Admin user ({admin_email}) password synced from environment.")
