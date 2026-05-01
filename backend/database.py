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
            client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=8000,
                connectTimeoutMS=8000,
                socketTimeoutMS=8000,
            )
            await client.admin.command('ping')
            print("MongoDB connected successfully.")
        except Exception as e:
            print(f"MongoDB primary connection failed: {e}. Trying without certifi...")
            try:
                client = AsyncIOMotorClient(
                    settings.MONGODB_URI,
                    serverSelectionTimeoutMS=8000,
                    connectTimeoutMS=8000,
                )
                await client.admin.command('ping')
                print("MongoDB connected (fallback).")
            except Exception as e2:
                print(f"MongoDB fallback also failed: {e2}. Continuing without DB.")

async def close_db():
    global client
    if client is not None:
        client.close()
        client = None
        print("MongoDB client closed.")

_db_initialized = False

async def get_db() -> AsyncIOMotorDatabase:
    global client, _db_initialized
    if client is None:
        await connect_db()
    if client is None:
        raise RuntimeError("Cannot connect to MongoDB. Check MONGODB_URI and Atlas IP allowlist.")
    db = client[DATABASE_NAME]
    if not _db_initialized:
        _db_initialized = True
        try:
            await init_db(db)
            await seed_admin(db)
        except Exception as e:
            _db_initialized = False
            print(f"DB lazy-init failed: {e}")
    return db

async def _safe_index(collection, keys, **kwargs):
    """Create index, silently dropping it first if options conflict."""
    try:
        await collection.create_index(keys, **kwargs)
    except Exception:
        try:
            await collection.drop_index(keys if isinstance(keys, str) else [(k, v) for k, v in ([keys] if isinstance(keys, tuple) else keys)])
            await collection.create_index(keys, **kwargs)
        except Exception as e:
            print(f"Index warning on {collection.name}: {e}")

async def init_db(db: AsyncIOMotorDatabase):
    await _safe_index(db.users, "email", unique=True)
    await _safe_index(db.user_credentials, "user_id")
    await _safe_index(db.user_credentials, [("user_id", 1), ("smtp_user", 1)], unique=True, sparse=True)
    await _safe_index(db.mail_templates, "user_id")
    await _safe_index(db.contact_lists, "user_id")
    await _safe_index(db.mail_jobs, [("user_id", 1), ("status", 1)])
    await _safe_index(db.mail_logs, [("user_id", 1), ("job_id", 1), ("sent_at", 1)])
    await _safe_index(db.audit_logs, [("user_id", 1), ("timestamp", 1)])
    await _safe_index(db.scheduled_tasks, [("user_id", 1), ("next_run", 1)])
    await _safe_index(db.reply_inbox, [("user_id", 1), ("received_at", 1), ("is_read", 1)])
    await _safe_index(db.revoked_tokens, "jti", unique=True)
    await _safe_index(db.revoked_tokens, "revoked_at", expireAfterSeconds=604800)
    print("Database indexes verified.")

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
