import os
import pathlib
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import settings
from database import connect_db, close_db, get_db
from services.scheduler_service import start_scheduler, stop_scheduler

# Routers
from routers.auth import router as auth_router
from routers.user import router as user_router
from routers.admin import router as admin_router
from routers.settings import router as settings_router
from routers.contacts import router as contacts_router
from routers.mail import router as mail_router
from routers.ai import router as ai_router
from routers.template import router as template_router
from routers.schedule import router as schedule_router
from routers.replies import router as replies_router

logger = logging.getLogger(__name__)

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On Vercel serverless each invocation is a fresh process — yield immediately
    # so the function starts accepting requests without waiting for DB/scheduler.
    # DB init (indexes + admin seed) runs lazily on the first get_db() call.
    # Scheduler is skipped on Vercel (no persistent process to run background jobs).
    is_vercel = bool(os.environ.get("VERCEL"))
    if not is_vercel:
        try:
            await connect_db()
            db = await get_db()
            try:
                await start_scheduler(db)
            except Exception as se:
                logger.error(f"Scheduler failed to start: {se}")
        except Exception as e:
            logger.error(f"Startup failed: {e}")
    yield
    if not is_vercel:
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

# Serve frontend static files (local dev). On Vercel, CDN handles this.
_public = pathlib.Path(__file__).parent / "public"
if _public.exists():
    app.mount("/", StaticFiles(directory=str(_public), html=True), name="static")

@app.get("/health", tags=["system"])
async def health_check():
    db_connected = False
    db_error = None
    try:
        db = await get_db()
        await db.command("ping")
        db_connected = True
    except Exception as e:
        db_error = str(e)

    return {
        "status": "ok" if db_connected else "degraded",
        "env": settings.APP_ENV,
        "db_connected": db_connected,
        "db_error": db_error,
    }
