from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
import certifi

class Database:
    client: AsyncIOMotorClient = None
    db = None

db_manager = Database()

async def connect_to_mongo():
    db_manager.client = AsyncIOMotorClient(settings.MONGODB_URI, tlsCAFile=certifi.where())
    db_manager.db = db_manager.client.get_database("bulkreach_pro")
    print("Connected to MongoDB Atlas")

async def close_mongo_connection():
    if db_manager.client:
        db_manager.client.close()
        print("Closed MongoDB connection")

def get_db():
    return db_manager.db
