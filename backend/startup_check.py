import os
import sys
import asyncio
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from motor.motor_asyncio import AsyncIOMotorClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_checks():
    load_dotenv()
    
    # 1. Test Encryption
    logger.info("Testing encryption...")
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        logger.error("ENCRYPTION_KEY is missing")
        sys.exit(1)
    try:
        f = Fernet(key.encode())
        test_msg = b"secret_test"
        enc = f.encrypt(test_msg)
        dec = f.decrypt(enc)
        assert dec == test_msg
        logger.info("Encryption round-trip passed.")
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        sys.exit(1)

    # 2. Test MongoDB
    logger.info("Testing MongoDB connection...")
    uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME", "bulkreach_prod")
    if not uri:
        logger.error("MONGODB_URI is missing")
        sys.exit(1)
    
    try:
        client = AsyncIOMotorClient(uri)
        db = client[db_name]
        collections = await db.list_collection_names()
        logger.info(f"Connected to DB: {db_name}. Collections: {collections}")
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        sys.exit(1)

    # 3. Check indexes
    expected_collections = ["users", "user_credentials", "contacts", "contact_lists", "templates", "mail_jobs", "mail_logs", "scheduled_tasks", "audit_log", "replies"]
    for c in expected_collections:
        if c not in collections:
            logger.warning(f"Collection {c} not found (will be created automatically)")
        else:
            idx = await db[c].index_information()
            logger.info(f"Collection {c} has indexes: {list(idx.keys())}")

    # 4. Check admin user
    logger.info("Verifying admin user...")
    admin_email = os.getenv("ADMIN_EMAIL")
    if admin_email:
        admin = await db.users.find_one({"email": admin_email})
        if admin:
            logger.info(f"Admin user {admin_email} exists.")
        else:
            logger.warning(f"Admin user {admin_email} not found. Ensure seeding runs on startup.")
            
    print("\n✓ All checks passed. Ready to deploy.")

if __name__ == "__main__":
    asyncio.run(run_checks())
