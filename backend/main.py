import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Add parent directory to path to allow imports from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import settings
from backend.database import connect_db, close_db, get_db, init_db, seed_admin
from backend.services.scheduler_service import start_scheduler, stop_scheduler

# Routers
from backend.routers.auth import router as auth_router
from backend.routers.user import router as user_router
from backend.routers.admin import router as admin_router
from backend.routers.settings import router as settings_router
from backend.routers.contacts import router as contacts_router
from backend.routers.mail import router as mail_router
from backend.routers.ai import router as ai_router
from backend.routers.template import router as template_router
from backend.routers.schedule import router as schedule_router
from backend.routers.replies import router as replies_router

logger = logging.getLogger(__name__)

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await connect_db()
        db = await get_db()
        await init_db(db)
        await seed_admin(db)
        # Only start scheduler if not in a simple serverless request context if possible, 
        # but try-except it anyway
        try:
            await start_scheduler(db)
        except Exception as se:
            logger.error(f"Scheduler failed to start: {se}")
    except Exception as e:
        logger.error(f"Startup sequence failed: {e}")
        
    yield
    # Shutdown
    try:
        await stop_scheduler()
        await close_db()
    except:
        pass

app = FastAPI(title="BulkReach Pro API", lifespan=lifespan)
app.state.limiter = limiter

# Exception Handlers
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# CORS — never combine allow_origins=["*"] with allow_credentials=True (Starlette rejects preflight with 400)
_raw_origins = settings.CORS_ORIGINS.strip() if settings.CORS_ORIGINS else ""
if _raw_origins and _raw_origins != "*":
    origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]
else:
    # Wildcard not allowed with credentials; enumerate the common dev + prod origins
    origins = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://localhost:4173",
    ]
    if settings.FRONTEND_URL:
        origins.append(settings.FRONTEND_URL.rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?|https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(user_router, prefix="/api/user", tags=["user"])
app.include_router(admin_router, prefix="/api/admin", tags=["admin"])
app.include_router(mail_router, prefix="/api/mail", tags=["mail"])
app.include_router(template_router, prefix="/api/template", tags=["template"])
app.include_router(contacts_router, prefix="/api/contacts", tags=["contacts"])
app.include_router(settings_router, prefix="/api/settings", tags=["settings"])
app.include_router(ai_router, prefix="/api/ai", tags=["ai"])
app.include_router(schedule_router, prefix="/api/schedule", tags=["schedule"])
app.include_router(replies_router, prefix="/api/replies", tags=["replies"])

@app.get("/health", tags=["system"])
async def health_check():
    db_connected = False
    try:
        db = await get_db()
        db_connected = db is not None
    except Exception:
        pass
        
    return {
        "status": "ok",
        "env": settings.APP_ENV,
        "db_connected": db_connected,
        "scheduler_running": True
    }
