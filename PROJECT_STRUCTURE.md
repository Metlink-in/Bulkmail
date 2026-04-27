# Project Structure

## Backend
- `backend/main.py` → FastAPI application entrypoint and lifespan configurator.
- `backend/config.py` → Settings mapping `.env` to Pydantic definitions.
- `backend/database.py` → Motor AsyncIO initialization and admin seeding.
- `backend/requirements.txt` → Pinned pip dependencies.
- `backend/render.yaml` → Render.com deployment manifest.
- `backend/startup_check.py` → Pre-flight sanity validation script testing cryptography and connections.
- `backend/utils/helpers.py` → Core Fernet hashing, JWT tools, and HTML Bleach sanitization.
- `backend/middleware/auth_middleware.py` → JWT Bearer validation and audit log recording.

### Models
- `backend/models/user.py` → User configurations and schemas.
- `backend/models/mail.py` → Mail logs and job metadata schemas.

### Services
- `backend/services/auth_service.py` → Authentication token management logic.
- `backend/services/validation_service.py` → Email regex formatting and MX resolving bounds.
- `backend/services/contact_service.py` → CSV and Google Sheets integrations.
- `backend/services/mail_service.py` → Core asynchronous mail engine managing batch processing and templates.
- `backend/services/ai_service.py` → Gemini AI prompt generation.
- `backend/services/scheduler_service.py` → APScheduler instance mappings.
- `backend/services/reply_service.py` → Thread-based IMAP syncing mechanism.

### Routers
- `backend/routers/auth.py` → Login, Register, Refresh endpoints.
- `backend/routers/user.py` → User profile and user telemetry tracking.
- `backend/routers/admin.py` → System oversight, live aggregation, and impersonation routes.
- `backend/routers/settings.py` → IMAP, SMTP, Gemini credential configurations.
- `backend/routers/contacts.py` → List endpoints and CSV file parsers.
- `backend/routers/mail.py` → Live job execution endpoints.
- `backend/routers/ai.py` → Compose endpoint execution.
- `backend/routers/template.py` → Email template CRUD logic.
- `backend/routers/schedule.py` → Cron triggers.
- `backend/routers/replies.py` → IMAP syncing endpoints.

## Frontend
- `frontend/vercel.json` → Serverless manifest configuring API proxies and headers.
- `frontend/dashboard.html` → Regular user command center.
- `frontend/admin.html` → High-level oversight panel for administrators.
- `frontend/index.html` → Landing page and marketing block.
- `frontend/login.html` & `register.html` → Authentication modals.
- `frontend/css/main.css` → Global `.var()` design configurations.
- `frontend/css/components.css` → Responsive module stylings for buttons, badges, tables.
- `frontend/css/dashboard.css` → Fixed sidebar layouts and stat grids.
- `frontend/js/api.js` → Base JSON client handler.
- `frontend/js/auth.js` → Live form validations.

### Pages
- `frontend/pages/admin-users.html` → Admin dashboard for tenant modifications.
- `frontend/pages/admin-logs.html` → Global audit trail ledger.
- `frontend/pages/admin-jobs.html` → Live global job queues.
- `frontend/pages/admin-live.html` → Aggregated system health tracking polling.
- `frontend/pages/admin-credentials.html` → Vault interface mapping integrations.
- `frontend/pages/bulk-mail.html` → Tri-pane email composer.
- `frontend/pages/contacts.html` → Contact list table mappings.
- `frontend/pages/history.html` → Track campaign stats natively.
- `frontend/pages/profile.html` → Basic user modification layer.
- `frontend/pages/replies.html` → Interactive inbox pane syncing with background tasks.
- `frontend/pages/schedule.html` → Management of Cron jobs mapping to recurring triggers.
- `frontend/pages/settings.html` → Global credentials manager per user.
- `frontend/pages/template-preview.html` → Interactive email preview grids.
