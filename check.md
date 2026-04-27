# BulkReach Pro — 10-Step Build Prompts (Gemini Flash 2.5)

> **How to use:** Feed the SYSTEM CONTEXT block once at the start of your Gemini session,
> then send each numbered prompt in order. Complete and verify each step before moving to the next.

---

## ─── SYSTEM CONTEXT (Send this FIRST in every new session) ───

```
You are a senior full-stack engineer building "BulkReach Pro" —
a multi-tenant bulk cold email outreach SaaS for AI and development agencies.

STACK: FastAPI · Motor (async MongoDB Atlas) · HTML/CSS/JS (vanilla) · JWT Auth · APScheduler · Gemini Flash 2.5 AI · aiosmtplib · Vercel deploy

RULES YOU MUST NEVER BREAK:
- Output COMPLETE files — no truncation, no "..." placeholders, no "add your logic here"
- Always use async Motor — NEVER sync pymongo
- Always filter MongoDB queries by user_id — never expose cross-tenant data
- Admin routes (/api/admin/*) always protected by require_admin() FastAPI Depends
- Encrypt all SMTP passwords and API keys using Fernet before storing
- Every function fully implemented — no stubs
- Pinned dependencies: fastapi==0.111.0, motor==3.4.0, python-jose==3.3.0,
  passlib==1.7.4, bcrypt==4.1.3, aiosmtplib==3.0.1,
  google-generativeai==0.5.4, apscheduler==3.10.4,
  cryptography==42.0.7, python-dotenv==1.0.1, dnspython==2.6.1,
  bleach==6.1.0, slowapi==0.1.9, pydantic-settings==2.2.1
```

---

## PROMPT 1 — Project Scaffold, Config & Database Foundation

```
PROJECT: BulkReach Pro — Step 1 of 10: Project Scaffold, Config & Database

Generate the following files completely with no truncation:

1. requirements.txt
   Pinned versions: fastapi==0.111.0, motor==3.4.0, python-jose[cryptography]==3.3.0,
   passlib[bcrypt]==1.7.4, bcrypt==4.1.3, aiosmtplib==3.0.1,
   google-generativeai==0.5.4, apscheduler==3.10.4, cryptography==42.0.7,
   python-dotenv==1.0.1, dnspython==2.6.1, bleach==6.1.0, slowapi==0.1.9,
   pydantic-settings==2.2.1, uvicorn[standard]==0.29.0, python-multipart==0.0.9,
   pandas==2.2.1, gspread==6.0.2, aiofiles==23.2.1

2. .env.example
   Include ALL these variables:
   MONGODB_URI, MONGODB_DB_NAME=bulkreach_prod,
   JWT_SECRET_KEY (min 32 chars note), JWT_ALGORITHM=HS256,
   ACCESS_TOKEN_EXPIRE_MINUTES=30, REFRESH_TOKEN_EXPIRE_DAYS=7,
   ENCRYPTION_KEY (Fernet base64 note),
   ADMIN_EMAIL=jiteshbawaskar05@gmail.com, ADMIN_PASSWORD=Jitesh001@,
   ADMIN_NAME=Jitesh Bawaskar,
   APP_ENV=development, BACKEND_URL=http://localhost:8000,
   FRONTEND_URL=http://localhost:3000,
   CORS_ORIGINS=http://localhost:3000,
   GEMINI_API_KEY= (optional global key)

3. backend/config.py
   Pydantic-settings BaseSettings class loading all .env vars.
   Single settings = Settings() instance exported at bottom.

4. backend/database.py
   Async Motor client. Functions:
   - get_database() → AsyncIOMotorDatabase
   - init_db(): creates all 9 collections with indexes:
     * users: unique index on email
     * user_credentials: unique index on user_id
     * mail_templates: index on user_id
     * contact_lists: index on user_id
     * mail_jobs: index on user_id + status
     * mail_logs: index on user_id + job_id + sent_at
     * audit_logs: index on user_id + timestamp
     * scheduled_tasks: index on user_id + next_run
     * reply_inbox: index on user_id + received_at + is_read
   - seed_admin(): checks if admin exists, if not creates with
     email=jiteshbawaskar05@gmail.com password=Jitesh001@ role=admin
     (bcrypt hashed password)

5. backend/models/user.py
   Pydantic v2 models: UserCreate, UserLogin, UserResponse, UserUpdate,
   UserInDB (with hashed_password, role, is_active, created_at, org_name)
   Role must be Literal["admin", "user"]

6. backend/models/mail.py
   Pydantic v2 models: MailJob, MailJobCreate, MailLog, MailLogResponse,
   MailSendRequest, MailStatusResponse
   Include all fields from database spec: status enum, scheduled_at,
   interval_seconds=300, contact_ids list

7. backend/models/template.py
   Pydantic v2: TemplateCreate, TemplateUpdate, TemplateResponse
   Fields: name, subject, html_body, user_id, created_at, updated_at

8. backend/models/contact.py
   Pydantic v2: Contact (email, name, org, custom_fields dict),
   ContactList, ContactListCreate, ContactImportResponse
   Include email_status: Literal["valid","invalid","risky","mx_fail"]

9. backend/models/schedule.py
   Pydantic v2: ScheduledTask, ScheduledTaskCreate, ScheduledTaskUpdate
   Fields: user_id, job_id, cron_expression, next_run, is_active,
   template_id, contact_ids, frequency, recurrence_type

10. backend/main.py
    FastAPI app with:
    - lifespan context: calls init_db() and seed_admin() on startup,
      starts APScheduler on startup, shuts down on stop
    - CORS middleware: allow CORS_ORIGINS from config
    - Include all routers (auth, user, admin, mail, template, contacts,
      settings, ai, schedule, replies) with /api prefix
    - slowapi rate limiter setup
    - Global exception handlers for 404, 422, 500
    - Health check: GET /health → {"status": "ok", "env": APP_ENV}

Output every file fully. No truncation.
```

---

## PROMPT 2 — Authentication System (JWT + Role Guards)

```
PROJECT: BulkReach Pro — Step 2 of 10: Authentication System

The database, models, and main.py from Step 1 are complete.
Now generate the complete authentication layer:

1. backend/utils/helpers.py
   Utility functions:
   - generate_token(length=32) → random URL-safe string
   - get_current_timestamp() → datetime UTC now
   - hash_password(plain: str) → bcrypt hash string
   - verify_password(plain: str, hashed: str) → bool
   - encrypt_secret(value: str, key: str) → Fernet encrypted string
   - decrypt_secret(encrypted: str, key: str) → plain string
   - sanitize_html(html: str) → bleach-cleaned HTML
     (allowed tags: p, br, b, i, u, h1, h2, h3, ul, ol, li, a, img,
      span, div, strong, em, table, tr, td, th, thead, tbody)
   - validate_email_format(email: str) → bool (RFC 5322 regex)

2. backend/services/auth_service.py
   Functions:
   - create_access_token(data: dict) → JWT string (30min expiry)
   - create_refresh_token(data: dict) → JWT string (7 days expiry)
   - verify_token(token: str) → decoded payload dict or raise 401
   - get_user_by_email(db, email: str) → user dict or None
   - authenticate_user(db, email, password) → user dict or None
   - register_user(db, UserCreate) → inserted user dict
     (check email unique, hash password, set role="user", is_active=True)
   - revoke_token(db, jti: str) → stores in revoked_tokens collection
   - is_token_revoked(db, jti: str) → bool

3. backend/middleware/auth_middleware.py
   FastAPI dependencies:
   - get_current_user(token: str = Depends(oauth2_scheme), db) → user dict
     Verifies JWT, checks not revoked, fetches user from DB, raises 401 if any fail
   - require_user(current_user = Depends(get_current_user)) → user dict
     Raises 403 if user is_active=False
   - require_admin(current_user = Depends(get_current_user)) → user dict
     Raises 403 if role != "admin" — hard block, no exceptions

4. backend/middleware/audit_middleware.py
   Function: log_audit(db, user_id, action, resource, detail, request)
   Saves to audit_logs collection with ip_address from request.
   Actions to log: login, logout, register, send_campaign,
   change_credentials, user_crud_by_admin, delete_campaign

5. backend/routers/auth.py
   POST /api/auth/register
   - Body: UserCreate (name, email, password, org_name)
   - Validates: email unique, password min 8 chars
   - Returns: {access_token, refresh_token, user: UserResponse}
   - Logs audit: action="register"

   POST /api/auth/login
   - Body: UserLogin (email, password)
   - Rate limited: 5 attempts per 15min per IP (slowapi)
   - Returns: {access_token, refresh_token, user: UserResponse}
   - Logs audit: action="login"

   POST /api/auth/refresh
   - Body: {refresh_token: str}
   - Returns new access_token if refresh_token valid

   POST /api/auth/logout
   - Requires: Bearer token
   - Revokes both access + refresh tokens (store jti in revoked_tokens)
   - Logs audit: action="logout"

   GET /api/auth/me
   - Requires: Bearer token
   - Returns: UserResponse (current user profile)

Output every file fully. No truncation.
```

---

## PROMPT 3 — Settings, Credentials & Email Validation Service

```
PROJECT: BulkReach Pro — Step 3 of 10: Settings, Credentials & Validation

Auth layer from Step 2 is complete.
Now generate:

1. backend/services/validation_service.py
   Async function validate_email(email: str) → dict:
   {
     email: str,
     status: "valid" | "invalid" | "risky" | "mx_fail",
     reason: str
   }
   Steps:
   a) Format check: RFC 5322 regex → "invalid" if fails
   b) Disposable domain check: blocklist of 50+ throwaway domains
      (mailinator, tempmail, guerrillamail, throwam, yopmail, etc.)
      → "risky" if matched
   c) MX record lookup using dnspython asyncresolver:
      await asyncresolver.resolve(domain, 'MX')
      → "mx_fail" if no MX records found or NXDOMAIN
   d) All pass → "valid"

   Also: async function validate_email_list(emails: list[str]) →
   list[dict] — runs all validations concurrently with asyncio.gather

2. backend/services/contact_service.py
   Functions:
   - async parse_csv(file_bytes: bytes) → list[Contact]
     Use pandas to parse, map columns: email, name, org, custom fields
     Run validate_email on each, attach status
   - async import_from_sheets(sheet_url: str, api_key: str, range: str)
     → list[Contact]
     Use gspread with service account or API key auth
     Parse rows same as CSV, run validation
   - async save_contact_list(db, user_id, name, contacts) → ContactList
   - async get_contact_lists(db, user_id) → list[ContactList]
   - async get_contact_list(db, user_id, list_id) → ContactList
   - async update_contact(db, user_id, contact_id, data) → Contact
   - async delete_contact_list(db, user_id, list_id) → bool

3. backend/routers/settings.py
   All routes require Depends(require_user):

   GET /api/settings
   Returns user's full settings (SMTP decrypted host/port/user only —
   NOT password, show masked "••••••••")

   POST /api/settings
   Body: full settings object (all tabs):
   {
     smtp_host, smtp_port, smtp_user, smtp_password,
     use_tls, use_ssl,
     imap_host, imap_port, imap_user, imap_password,
     fetch_interval_minutes,
     gemini_api_key,
     from_name, reply_to_email,
     email_delay_seconds (min 60, default 300),
     daily_send_limit, warmup_mode, unsubscribe_footer,
     google_sheets_api_key, default_sheet_id
   }
   Encrypts smtp_password, imap_password, gemini_api_key before save
   Upserts into user_credentials by user_id

   POST /api/settings/smtp/test
   Decrypts SMTP creds, attempts aiosmtplib connect + EHLO
   Returns: {success: bool, message: str, latency_ms: int}

   POST /api/settings/imap/test
   Tests IMAP connection using imaplib.IMAP4_SSL in thread executor
   Returns: {success: bool, message: str, folder_count: int}

   POST /api/settings/ai/test
   Calls Gemini API with test prompt "Say hello in one word"
   Returns: {success: bool, message: str, model: str}

   POST /api/settings/sheets/test
   Tests Google Sheets access with provided api_key + sheet_id
   Returns: {success: bool, message: str, sheet_title: str}

4. backend/routers/contacts.py
   All routes require Depends(require_user):

   GET /api/contacts → list of user's contact lists (paginated)
   POST /api/contacts → create empty contact list
   GET /api/contacts/{list_id} → single list with all contacts
   PUT /api/contacts/{list_id} → update list name
   DELETE /api/contacts/{list_id} → delete list

   POST /api/contacts/import/csv
   Accepts: multipart file upload
   Calls contact_service.parse_csv, saves, returns ContactImportResponse
   (total, valid_count, invalid_count, risky_count)

   POST /api/contacts/import/sheets
   Body: {sheet_url, range, list_name}
   Gets user's google_sheets_api_key from settings, calls import_from_sheets

   PUT /api/contacts/{list_id}/contacts/{contact_id}
   Update single contact fields

   DELETE /api/contacts/{list_id}/contacts/{contact_id}
   Remove single contact from list

   POST /api/contacts/validate
   Body: {emails: list[str]}
   Runs validate_email_list, returns results immediately

Output every file fully. No truncation.
```

---

## PROMPT 4 — Mail Engine, Anti-Spam & Send Service

```
PROJECT: BulkReach Pro — Step 4 of 10: Mail Engine & Anti-Spam Service

Steps 1–3 complete. Now build the core mail sending engine.

1. backend/services/mail_service.py
   This is the most critical file. Implement fully:

   CONSTANTS:
   MIN_DELAY_SECONDS = 60
   DEFAULT_DELAY_SECONDS = 300
   SPAM_WORDS = [...] (list of 30+ common spam trigger words:
   "free", "winner", "urgent", "click here", "act now", "limited time",
   "guaranteed", "no risk", "earn money", "make money", "cash", "prize",
   "congratulations", "you've been selected", "double your", etc.)

   async def get_user_smtp_settings(db, user_id) → dict
   Fetches from user_credentials, decrypts smtp_password

   async def build_email_message(
     to_email, to_name, subject, html_body, from_name, from_email,
     reply_to, message_id_domain, personalization_data: dict,
     attachments: list
   ) → email.mime.multipart.MIMEMultipart
   - Replaces {first_name}, {last_name}, {company}, {custom_1..5}
     in subject and html_body
   - Appends unsubscribe footer if enabled in settings
   - Sets headers: Message-ID, X-Mailer, List-Unsubscribe,
     Content-Type, MIME-Version
   - Adds HTML and plain-text alternative parts
   - Attaches any files from attachments list

   def check_subject_for_spam(subject: str) → dict
   Returns {has_spam: bool, flagged_words: list[str], score: int}

   async def send_single_email(
     smtp_settings: dict, message: MIMEMultipart, to_email: str
   ) → dict  → {success: bool, message_id: str, error: str|None}
   Uses aiosmtplib with TLS/SSL based on settings
   Catches: SMTPException, ConnectionError, timeout (30s)
   Returns structured result for logging

   async def process_mail_job(db, job_id: str)
   Main job runner — called by scheduler:
   a) Fetch job from mail_jobs, set status="running"
   b) Fetch all contacts for this job
   c) Fetch template, user smtp settings, user send settings
   d) Check daily send limit — if reached, pause + update job status
   e) Filter out already-sent recipients (check mail_logs for job_id)
   f) For each unsent contact:
      - Validate email (skip if invalid, log as invalid)
      - Build personalized message
      - Send via send_single_email
      - Log result to mail_logs (status, sent_at, message_id, error)
      - Log audit entry
      - Wait delay_seconds (from settings, floor MIN_DELAY_SECONDS)
      - Check if job paused/cancelled mid-run (re-fetch job status)
      - If paused: break loop, save progress
   g) When all done: set job status="done", completed_at=now
   h) Handle warmup_mode: if enabled, enforce daily ramp limits

   async def pause_job(db, user_id, job_id) → bool
   async def resume_job(db, user_id, job_id) → bool
   async def cancel_job(db, user_id, job_id) → bool
   (all verify user_id ownership before changing status)

   async def get_job_status(db, user_id, job_id) → dict
   Returns: {status, sent_count, failed_count, total_count,
             current_recipient, progress_pct, started_at, elapsed_seconds}

2. backend/services/scheduler_service.py
   APScheduler AsyncIOScheduler setup:

   scheduler = AsyncIOScheduler()

   async def start_scheduler(db): starts scheduler
   async def stop_scheduler(): shuts down

   async def schedule_job(db, job_id: str, run_at: datetime)
   Adds one-time job to scheduler: calls process_mail_job at run_at

   async def schedule_recurring(db, task_id: str, cron_expression: str)
   Adds CronTrigger job. On each fire: creates new mail_job from
   scheduled_task config, then calls process_mail_job.

   async def cancel_scheduled_job(job_id: str)
   async def get_all_scheduled_jobs() → list of job info dicts

   async def check_and_queue_pending_jobs(db)
   Runs every 1 minute via IntervalTrigger:
   Finds mail_jobs with status="queued" and scheduled_at <= now,
   calls process_mail_job for each.

3. backend/routers/mail.py
   All routes require Depends(require_user):

   POST /api/mail/jobs
   Body: MailJobCreate (template_id, contact_list_id, schedule_at|null,
         interval_seconds, daily_limit, from_name_override,
         reply_to_override, attachments_base64)
   Creates job in mail_jobs with status="queued"
   If schedule_at is null → schedule immediately (run_at = now + 5s)
   If schedule_at set → schedule for that datetime
   Returns: {job_id, status, total_recipients, scheduled_at}

   GET /api/mail/jobs
   Returns paginated list of user's jobs with summary stats

   GET /api/mail/jobs/{job_id}
   Returns full job details + recent 20 log entries

   GET /api/mail/jobs/{job_id}/status
   Returns get_job_status() — lightweight for polling every 10s

   POST /api/mail/jobs/{job_id}/pause
   POST /api/mail/jobs/{job_id}/resume
   POST /api/mail/jobs/{job_id}/cancel

   POST /api/mail/test
   Body: {to_email, template_id}
   Sends single test email immediately, no logging to job
   Returns: {success, message_id, error}

   GET /api/mail/logs
   Query params: page, limit, job_id, status, start_date, end_date, search
   Returns paginated mail_logs for current user

Output every file fully. No truncation.
```

---

## PROMPT 5 — AI Compose, Templates & Schedule Router

```
PROJECT: BulkReach Pro — Step 5 of 10: AI Compose, Templates & Schedules

Steps 1–4 complete. Now build AI service, template management, and scheduling.

1. backend/services/ai_service.py
   import google.generativeai as genai

   async def compose_email(
     db, user_id: str,
     goal: str, industry: str, tone: str,
     sender_name: str, sender_company: str,
     value_prop: str, recipient_name: str = "there"
   ) → dict

   Steps:
   a) Fetch user's gemini_api_key from user_credentials (decrypted)
      If not set, try global GEMINI_API_KEY from config
      If neither: raise 400 "No Gemini API key configured"
   b) Configure genai.configure(api_key=...)
   c) model = genai.GenerativeModel("gemini-2.5-flash")
   d) Build this exact prompt (fill in variables):

   PROMPT = """
   You are an expert B2B cold email copywriter.
   Write a cold outreach email with:
   - Goal: {goal}
   - Target industry: {industry}
   - Tone: {tone}
   - From: {sender_name} at {sender_company}
   - Value proposition: {value_prop}

   Requirements:
   - Subject: under 60 chars, no spam trigger words, curiosity-driven
   - Body: 3-4 short paragraphs, under 200 words total
   - Opening: personalized with {first_name} placeholder
   - One clear CTA in last paragraph
   - Professional signature with {sender_name} and {sender_company}
   - NO ALL CAPS, max 1 exclamation mark in entire email
   - NO spam words: free, winner, urgent, guaranteed, limited time, act now

   Return ONLY valid JSON (no markdown, no backticks, just raw JSON):
   {{
     "subject": "...",
     "html_body": "...",
     "plain_text": "...",
     "preview_text": "...",
     "word_count": 0,
     "estimated_read_seconds": 0
   }}
   html_body must be complete HTML with inline CSS styles for email clients.
   """

   e) response = await asyncio.to_thread(model.generate_content, PROMPT)
   f) Parse JSON from response.text — strip any code fences if present
   g) Validate parsed JSON has all required keys
   h) Return parsed dict

2. backend/routers/ai.py
   POST /api/ai/compose   [Depends(require_user)]
   Body: {goal, industry, tone, sender_name, sender_company,
          value_prop, recipient_name}
   Calls ai_service.compose_email
   Returns: {subject, html_body, plain_text, preview_text,
             word_count, estimated_read_seconds}

   POST /api/ai/improve   [Depends(require_user)]
   Body: {current_subject, current_html_body, instruction}
   Sends current email + instruction to Gemini to improve it
   Same return format as compose

3. backend/routers/template.py
   All routes require Depends(require_user):

   GET /api/template
   Returns all user's templates (paginated, 20 per page)
   Include: id, name, subject, preview_text (first 100 chars stripped HTML),
            created_at, updated_at

   POST /api/template
   Body: TemplateCreate {name, subject, html_body}
   Sanitizes html_body with bleach before save
   Returns: TemplateResponse

   GET /api/template/{template_id}
   Returns full template with html_body

   PUT /api/template/{template_id}
   Body: TemplateUpdate {name?, subject?, html_body?}
   Sanitizes html_body, updates updated_at

   DELETE /api/template/{template_id}
   Hard delete, only if owned by current user

   POST /api/template/{template_id}/duplicate
   Creates a copy with name "Copy of {original_name}"

4. backend/routers/schedule.py
   All routes require Depends(require_user):

   GET /api/schedule
   Returns user's scheduled tasks, sorted by next_run asc

   POST /api/schedule
   Body: ScheduledTaskCreate {name, template_id, contact_list_id,
         recurrence_type: "once"|"daily"|"weekly"|"custom",
         cron_expression (if custom), run_at (if once),
         time_of_day (HH:MM for daily/weekly), day_of_week (if weekly)}
   Converts to cron_expression, calls scheduler_service.schedule_recurring
   Saves to scheduled_tasks collection

   GET /api/schedule/{task_id}
   Full task detail with last 10 executions from mail_jobs

   PUT /api/schedule/{task_id}
   Update template, contact list, or timing. Reschedules APScheduler job.

   DELETE /api/schedule/{task_id}
   Cancels APScheduler job, deletes from DB

   POST /api/schedule/{task_id}/pause
   Sets is_active=False, pauses APScheduler job

   POST /api/schedule/{task_id}/resume
   Sets is_active=True, re-adds APScheduler job

5. backend/routers/replies.py
   All routes require Depends(require_user):

   POST /api/replies/sync
   Triggers manual IMAP fetch for current user (runs in background task)
   Returns: {message: "Sync started", task_id}

   GET /api/replies
   Query: page, limit, is_read, job_id, search, start_date, end_date
   Returns paginated reply_inbox for current user

   GET /api/replies/{reply_id}
   Full reply detail. Marks as read (is_read=True).

   PUT /api/replies/{reply_id}/read
   Mark single reply as read

   POST /api/replies/read-all
   Mark all unread as read for current user

   DELETE /api/replies/{reply_id}
   Soft delete (set is_deleted=True)

   GET /api/replies/unread-count
   Returns {count: int} — for sidebar badge

   Also add: backend/services/reply_service.py
   async def fetch_replies_for_user(db, user_id: str):
   a) Get user IMAP settings (decrypted)
   b) Connect with imaplib.IMAP4_SSL in thread executor
   c) Search INBOX for emails from last fetch timestamp
   d) Parse each email: from, subject, body, date, message_id
   e) Try to match message_id to original sent email in mail_logs
      (look for In-Reply-To header matching our sent Message-IDs)
   f) Save new replies to reply_inbox (skip duplicates by message_id)
   g) Update last_imap_sync timestamp in user_credentials

Output every file fully. No truncation.
```

---

## PROMPT 6 — Admin Router & Live Monitoring

```
PROJECT: BulkReach Pro — Step 6 of 10: Admin Router & Live Monitoring

Steps 1–5 complete. Now build the complete admin backend layer.

1. backend/routers/user.py  (regular user self-service)
   All require Depends(require_user):

   GET /api/user/profile → UserResponse
   PUT /api/user/profile
   Body: {name?, org_name?, current_password?, new_password?}
   If changing password: verify current_password first
   Updates user in users collection

   GET /api/user/stats
   Returns aggregated stats for current user:
   {
     total_sent_all_time: int,
     sent_today: int,
     active_schedules: int,
     queued_jobs: int,
     failed_last_7_days: int,
     reply_rate_percent: float,
     top_performing_template: {name, open_rate}
   }
   Aggregate from mail_logs and scheduled_tasks for this user_id only.

   GET /api/user/activity
   Last 20 audit_log entries for current user

2. backend/routers/admin.py
   ALL routes require Depends(require_admin):

   ── User Management ──
   GET /api/admin/users
   Query: page=1, limit=25, search (email/name), is_active filter
   Returns paginated users list with stats per user
   (total sent, last login, active jobs count)

   GET /api/admin/users/{user_id}
   Full user profile + usage stats

   POST /api/admin/users
   Create user account directly (admin onboards org clients)
   Body: UserCreate + role field

   PUT /api/admin/users/{user_id}
   Update name, email, org_name, is_active, role

   DELETE /api/admin/users/{user_id}
   Hard delete user + all their data (cascade: jobs, logs, templates,
   contacts, settings, replies, schedules)
   Log this action in audit_logs.

   POST /api/admin/users/{user_id}/deactivate
   Sets is_active=False (soft block — they can't login)

   POST /api/admin/users/{user_id}/activate
   Sets is_active=True

   ── System Oversight ──
   GET /api/admin/stats
   System-wide stats:
   {
     total_users, active_users, new_users_today, new_users_this_week,
     total_emails_sent_all_time, total_emails_today,
     active_jobs_running, failed_jobs_last_24h,
     total_schedules_active, emails_per_hour_last_24h: [array of 24 values],
     top_active_users: [{name, email, sent_today}] (top 5)
   }

   GET /api/admin/logs
   Query: page, limit, user_id, action, start_date, end_date, ip_address
   Returns paginated audit_logs — all users

   GET /api/admin/mail-jobs
   All mail jobs across all users
   Query: page, limit, user_id, status, start_date, end_date
   Returns jobs with user_name and user_email included

   GET /api/admin/mail-logs
   All mail send logs across all users (paginated, filterable)

   ── Credentials Monitor ──
   GET /api/admin/users/{user_id}/settings
   Returns user's settings — passwords shown as "••••••••" (8 dots)
   smtp_host, smtp_port, smtp_user visible; passwords masked
   imap_host, imap_port visible; password masked
   gemini_api_key: show last 6 chars only (rest masked)
   google_sheets_api_key: show last 6 chars only

   ── Live Monitoring ──
   GET /api/admin/live
   Returns snapshot of current system state (for polling every 5s):
   {
     timestamp: ISO string,
     running_jobs: [{job_id, user_name, user_email, template_name,
                     sent, total, current_recipient, started_at}],
     queued_jobs_count: int,
     emails_sent_last_minute: int,
     emails_sent_last_hour: int,
     errors_last_hour: int,
     active_users_online: int
   }

   GET /api/admin/users/{user_id}/impersonate
   Admin can view data as if they were that user
   Returns a short-lived (5min) access token with user's role
   but with admin_impersonating: true claim in JWT
   (read-only — cannot send emails while impersonating)

Output every file fully. No truncation.
```

---

## PROMPT 7 — Frontend Foundation: CSS Design System + Shared JS

```
PROJECT: BulkReach Pro — Step 7 of 10: Frontend Foundation

Backend complete from Steps 1–6. Now build the entire frontend foundation.

1. frontend/css/main.css
   Complete CSS with:
   :root variables:
   --primary: #2563EB, --primary-dark: #1D4ED8, --primary-light: #EFF6FF
   --accent: #10B981, --accent-dark: #059669
   --danger: #EF4444, --warning: #F59E0B, --success: #10B981
   --info: #3B82F6
   --bg-primary: #FFFFFF, --bg-secondary: #F8FAFC, --bg-tertiary: #F1F5F9
   --bg-sidebar: #1E293B, --bg-sidebar-hover: #334155
   --text-primary: #0F172A, --text-secondary: #64748B, --text-muted: #94A3B8
   --text-sidebar: #CBD5E1, --text-sidebar-active: #FFFFFF
   --border: #E2E8F0, --border-focus: #2563EB
   --radius-sm: 4px, --radius-md: 8px, --radius-lg: 12px, --radius-xl: 16px
   --shadow-sm: 0 1px 3px rgba(0,0,0,0.08)
   --shadow-md: 0 4px 16px rgba(0,0,0,0.1)
   --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif
   --sidebar-width: 240px
   --transition: 150ms ease

   Admin override class .admin-mode:
   --bg-primary: #111111, --bg-secondary: #1A1A1A, --bg-tertiary: #0D0D0D
   --bg-sidebar: #0A0A0A, --bg-sidebar-hover: #1F1F1F
   --text-primary: #F1F1F1, --text-secondary: #A0A0A0
   --border: #2A2A2A, --admin-accent: #FF6B35

   CSS reset (box-sizing, margin 0, padding 0)
   Typography: Inter from Google Fonts import at top
   Body: font-family var(--font-sans), bg var(--bg-tertiary), color var(--text-primary)
   Scrollbar styling (thin, themed)
   Transitions on all interactive elements

2. frontend/css/components.css
   Complete component styles for:
   - .btn, .btn-primary, .btn-secondary, .btn-danger, .btn-ghost, .btn-sm, .btn-lg
     (with :hover, :active, :disabled states, loading spinner variant)
   - .input, .input-group, .input-label (floating label), .input-error
   - .card (white bg, shadow-sm, radius-lg, padding 24px)
   - .badge (pill), .badge-success, .badge-danger, .badge-warning, .badge-info, .badge-neutral
   - .table-container, .table, .table th, .table td, alternating rows
   - .modal-backdrop, .modal, .modal-header, .modal-body, .modal-footer
   - .toast-container, .toast, .toast-success, .toast-danger, .toast-warning
     (slide in from top-right, auto-dismiss)
   - .progress-bar-container, .progress-bar, .progress-bar-fill (animated shimmer)
   - .stat-card (icon, number large 32px bold, label, optional trend badge)
   - .empty-state (centered icon + message + optional CTA)
   - .spinner, .spinner-sm, .spinner-lg (CSS-only rotating ring)
   - .tabs, .tab-item (underline style), .tab-content
   - .dropdown, .dropdown-menu, .dropdown-item
   - .toggle (custom checkbox toggle switch)
   - .pagination (prev/next + page numbers)
   - .search-input (with search icon inside)
   - .alert (info/success/warning/danger variants with icon)

3. frontend/css/dashboard.css
   Layout styles:
   - .dashboard-layout: CSS grid, sidebar + main
   - .sidebar: fixed left, 240px, bg-sidebar, full height, flex column
   - .sidebar-logo: top section with logo text
   - .sidebar-nav: flex-column, gap 4px
   - .sidebar-nav-item: padding 10px 16px, radius-md, text-sidebar, hover bg-sidebar-hover
   - .sidebar-nav-item.active: bg-primary, text-white, font-weight 500
   - .sidebar-nav-item icon: 18px, margin-right 10px
   - .sidebar-user: bottom of sidebar, user avatar + name + role badge
   - .main-content: margin-left 240px, min-height 100vh, padding 32px
   - .page-header: flex row, title left, actions right, margin-bottom 24px
   - .stats-grid: CSS grid 4 columns (responsive: 2 on tablet, 1 on mobile)
   - Responsive: sidebar collapses to icons-only on < 768px
     hamburger toggle shows full sidebar as overlay on mobile

4. frontend/js/api.js
   Centralized API client:

   const API_BASE = window.location.origin + '/api';  // proxied via Vercel

   function getTokens() → {access, refresh} from localStorage
   function setTokens(access, refresh) → saves to localStorage
   function clearTokens() → removes from localStorage
   function isLoggedIn() → bool (checks access token exists + not expired)
   function getTokenPayload() → decoded JWT payload (base64 decode middle part)
   function getUserRole() → "admin"|"user" from token payload

   async function refreshAccessToken() → new access token or null
   Uses POST /api/auth/refresh. If fails → clearTokens() + redirect /login.html

   async function apiRequest(method, path, body, options) → response data
   Injects Authorization: Bearer header automatically
   On 401: tries refreshAccessToken() once, retries request
   On second 401: clearTokens(), redirect login
   Throws structured error: {status, message, detail}

   Shorthand: api.get(path), api.post(path, body), api.put(path, body),
   api.delete(path), api.upload(path, formData)

   function requireAuth() → call at top of every protected page
   Checks isLoggedIn(). If false → redirect /login.html

   function requireAdmin() → call at top of admin pages
   Checks getUserRole() === "admin". If false → redirect /dashboard.html

5. frontend/js/auth.js
   Handles login.html and register.html:

   Login flow:
   - Form submit → api.post('/auth/login', {email, password})
   - On success: setTokens, check role, redirect
   - On error: show inline error message, shake animation
   - Show/hide password toggle
   - Loading spinner on submit button

   Register flow:
   - Form submit → api.post('/auth/register', {name, email, password, org_name})
   - Password strength indicator (weak/medium/strong/very-strong)
   - Confirm password match validation
   - On success: auto-login (save tokens) → redirect dashboard

   Both:
   - Input validation before submit (required, email format, min length)
   - Disable submit while loading
   - Generic error display from API response

6. frontend/index.html
   Professional SaaS landing page:
   - Google Fonts Inter import
   - Navbar: "BulkReach Pro" logo left, Login + Get Started buttons right
     Sticky on scroll with slight shadow
   - Hero section: dark bg (#0D1117), headline "Scale Your Outreach.
     Land Every Inbox.", sub "AI-powered bulk email for agencies sending
     1000s of personalized cold emails daily", two CTAs
     Right side: animated email sending mockup (pure CSS/JS)
   - Stats bar: 3 numbers (10K+ emails/day, 99.2% deliverability, 5 min setup)
   - Features grid (3 col): AI Compose, Smart Scheduling, Anti-Spam Engine,
     Reply Tracking, Team Dashboard, CSV + Sheets Import
   - How it works: 3 steps numbered (Import contacts → Compose with AI → Send & Track)
   - Footer: links + copyright
   - Links Login → /login.html, Get Started → /register.html

7. frontend/login.html + frontend/register.html
   Clean centered card layout (400px max-width)
   Logo at top, form, switch to register/login link
   Includes api.js and auth.js

Output every file fully. No truncation.
```

---

## PROMPT 8 — User Dashboard Pages (All 8 Sidebar Pages)

```
PROJECT: BulkReach Pro — Step 8 of 10: User Dashboard & All User Pages

Frontend foundation from Step 7 complete. Build all user-facing dashboard pages.

Generate ALL of these complete HTML + inline JS files:

1. frontend/dashboard.html
   - requireAuth() check on load
   - Sidebar with all 9 nav links (icons + labels)
   - Dynamically load stats from GET /api/user/stats
   - 6 stat cards with animated count-up: Total Sent, Sent Today,
     Active Schedules, In Queue, Reply Rate, Failed Sends
   - Recent Activity feed (last 5 audit events)
   - Recent Campaigns table (last 5 jobs with status badges)
   - Quick action buttons: New Campaign, Import Contacts, New Template
   - Welcome message with user name from token payload

2. frontend/pages/bulk-mail.html
   This is the most complex page — generate completely:

   Section A — Email Composer:
   - Subject input with spam score indicator (live JS check)
   - Toolbar: Bold, Italic, Underline, H2, Link, Image URL, List buttons
     acting on contenteditable div
   - contenteditable div for HTML body (styled to look like email preview)
   - Template selector dropdown (loads from GET /api/template)
   - "Save as Template" button opens modal with name input
   - Character/word count display

   AI Compose Panel (collapsible drawer right side):
   - Fields: goal textarea, industry input, tone dropdown, sender_name,
     sender_company, value_prop textarea
   - "Generate Email" button → POST /api/ai/compose
   - Loading skeleton while generating (3s typical)
   - On success: auto-fill subject + html body in composer
   - "Improve Email" button to send current email back to AI with instructions

   Section B — Recipients:
   - Radio: Saved List | Upload CSV | Google Sheets
   - Saved List: dropdown of contact lists + count badge
   - CSV: drag-drop zone with file icon, shows parsed preview table
   - Sheets: URL input + range input + Test button
   - Preview table: email, name, org, validation badge (✓/✗/⚠)
   - "Validate All" button → POST /api/contacts/validate
   - Stats: X valid, Y invalid, Z risky — filter toggles

   Section C — Send Config:
   - Delay slider: 1–30 min (labels at 5, 10, 15, 30)
   - Schedule radio: Now | Later (datetime-local input)
   - Daily limit input
   - From name override
   - Reply-to override
   - File attachments: multi-file picker, shows list of attached files

   Section D — Controls:
   - "Start Campaign" primary button
   - After start: progress bar (polls /api/mail/jobs/{id}/status every 10s)
   - Live log feed: scrolling list of last 10 events
   - Pause / Resume / Cancel buttons (shown based on job status)
   - Campaign name input (auto-generated as "Campaign {date}" default)

   Sub-navigation tabs at top:
   [Compose] [History] [Preview] [Contacts] [Schedule]
   (tabs show/hide sections within same page)

3. frontend/pages/history.html
   - requireAuth() on load
   - Filter bar: date range pickers, status dropdown, search box
   - Jobs table: name, date, total, sent, failed, status badge, actions
   - Row expand (click): sub-table of individual sends per recipient
   - Export CSV button → download current filtered results
   - Pagination component (25/page)
   - Stat summary bar: total filtered results

4. frontend/pages/template-preview.html
   - Load template by ?id= query param or show blank
   - Split view: left editor pane, right preview iframe
   - Editor: textarea for raw HTML + subject input
   - Preview: renders in sandboxed iframe, refreshes on blur
   - Variable preview panel: input sample values for {first_name}, {company}
     → Show Preview button re-renders with substitutions
   - Mobile/desktop toggle (resize preview iframe width)
   - Send Test Email: modal with email input → POST /api/mail/test
   - Save button → POST or PUT /api/template

5. frontend/pages/contacts.html
   - List of contact lists as cards (name, count, source icon, created date)
   - "New List" button → modal with name input
   - Click card → expand to show contacts table
   - Import buttons: CSV upload, Google Sheets
   - Per contact row: email, name, org, validation badge, last contacted, edit/delete
   - Bulk select → Delete selected, Export selected
   - Assign to Schedule button (opens schedule picker modal)

6. frontend/pages/schedule.html
   - Calendar widget (month view, pure JS — show events as dots)
   - Below: list view of all schedules
   - Each schedule: name, template badge, contact list badge, next_run, status toggle
   - "New Schedule" button → full form modal:
     template dropdown, contact list dropdown, recurrence radio,
     time picker, day-of-week checkboxes (if weekly)
   - Edit, Pause/Resume, Delete actions per schedule

7. frontend/pages/profile.html
   - Avatar: large initials-based circle (color derived from email hash)
   - Display: name, email, org, role badge, member since
   - Edit mode toggle: in-place form editing
   - Change password section (current + new + confirm)
   - Activity summary cards: total campaigns, total emails sent
   - Save → PUT /api/user/profile

8. frontend/pages/settings.html
   - 5 tabs: SMTP | IMAP | AI | Email Safety | Google Sheets
   - Load existing settings on page open (GET /api/settings)
   - Each tab: form fields matching Step 3 spec
   - Passwords show as masked, toggle "show" eye icon
   - Test Connection button per tab → show result inline (green/red)
   - Save All Settings button → POST /api/settings
   - Unsaved changes indicator (yellow dot in tab label)

9. frontend/pages/replies.html
   - Unread count badge in sidebar nav
   - Filter bar: all/unread, search, date range, campaign filter
   - Inbox table: from, subject, received_at, campaign badge, read dot
   - Click row: slide-in panel (right drawer) with full email body in iframe
   - Mark read, mark unread, delete controls
   - "Sync Now" button → POST /api/replies/sync, shows loading
   - Pagination

For ALL pages:
- Include api.js, implement requireAuth() at top
- Toast notifications for all success/error states
- Loading skeletons while data fetches
- Empty states with helpful message and CTA
- Responsive (sidebar collapses on mobile)

Output every file fully. No truncation.
```

---

## PROMPT 9 — Admin Dashboard (All Admin Pages)

```
PROJECT: BulkReach Pro — Step 9 of 10: Admin Dashboard & All Admin Pages

User dashboard from Step 8 complete. Now build the complete admin interface.
Admin theme: dark (#0D0D0D), orange accent (#FF6B35). Visually DISTINCT from user UI.

1. frontend/admin.html
   - requireAdmin() check on load (redirect /dashboard.html if not admin)
   - Dark sidebar: bg #0A0A0A, "ADMIN PANEL" badge in orange at top
   - Admin nav links (all user links + admin-only):
     Overview | Users | All Jobs | All Logs | Credentials | Live Monitor |
     ── same as user: Templates | Contacts | Bulk Mail | Schedule | Replies
   - "Logged in as admin" indicator with admin email
   - Overview stats cards (6): Total Users, Active Users, System Emails Today,
     Running Jobs, Failed Last 24h, Replies Fetched Today
   - Emails per hour chart: last 24h bar chart (pure JS canvas)
   - Top Active Users table: rank, name, email, sent today, status
   - System health row: MongoDB ping, Scheduler status, SMTP test status

2. frontend/pages/admin-users.html
   - requireAdmin() on load
   - Search bar + filters: status (active/inactive), role, date joined
   - Users table: avatar, name, email, org, role badge, joined, last login,
     sent total, status badge, action dropdown
   - Action dropdown per user: View Profile | Edit | Deactivate | Delete |
     View Settings | View Jobs | Impersonate (view-only)
   - "Create User" button → modal with full UserCreate form + role selector
   - Bulk actions: select multiple → Deactivate selected, Delete selected
   - Pagination (25/page)
   - Click user row → slide-in detail panel:
     Full profile, usage stats, last 10 campaigns, settings overview (masked)

3. frontend/pages/admin-logs.html
   - requireAdmin() on load
   - Filter bar: user search, action type dropdown, date range, IP address
   - Logs table: timestamp, user (name+email), action, resource, detail, IP
   - Color-coded action badges: login=blue, send=green, error=red, crud=amber
   - Export to CSV button
   - Auto-refresh toggle (refresh every 30s)
   - Pagination

4. frontend/pages/admin-jobs.html
   - All mail jobs across all users
   - Filter: user, status (queued/running/done/failed/paused), date range
   - Jobs table: user, campaign name, template, recipients, sent, failed,
     status badge, started_at, actions
   - Click row → full job detail modal with per-recipient log
   - Admin can cancel/pause any running job (admin override)
   - Export results CSV

5. frontend/pages/admin-live.html
   - requireAdmin() on load
   - "LIVE" red pulsing badge in page title
   - Auto-refresh every 5 seconds (calls GET /api/admin/live)
   - Running Jobs panel: real-time cards per active job
     (user, template, progress bar animated, current recipient, elapsed time)
   - System metrics row: emails/min, emails/hr, errors/hr
   - Activity feed: scrolling list of last 50 send events across all users
     (live appended, newest at top)
   - Active connections count
   - Quick stats: queue depth, avg send time
   - Pause All button (emergency stop — pauses all running jobs system-wide)
   - Refresh interval selector: 5s | 10s | 30s

6. frontend/pages/admin-credentials.html
   - requireAdmin() on load
   - Users list with expand per user
   - Expanded: SMTP host/port/user (visible), password "••••••••"
     IMAP host/port (visible), password "••••••••"
     Gemini key: "••••••" + last 6 chars
     Sheets key: "••••••" + last 6 chars
   - Last updated timestamp
   - "Request Reset" button (logs admin action, user gets notified)
   - Search/filter by user

For ALL admin pages:
- Dark theme applied (class="admin-mode" on body)
- Orange accent for active states, CTAs
- "ADMIN" breadcrumb in page header
- requireAdmin() at top of every page
- All API calls through api.js with Bearer token
- Toast notifications styled in orange theme
- Loading skeletons on data fetch
- Confirm dialog (custom modal) for destructive actions (delete, deactivate)

Output every file fully. No truncation.
```

---

## PROMPT 10 — Deployment Config, Final Wiring & Production Checklist

```
PROJECT: BulkReach Pro — Step 10 of 10: Deployment, Config & Production Wiring

All backend and frontend files from Steps 1–9 are complete.
Now generate all deployment, configuration, and final wiring files.

1. frontend/vercel.json
   {
     "rewrites": [
       {
         "source": "/api/:path*",
         "destination": "https://YOUR_BACKEND_URL/api/:path*"
       }
     ],
     "headers": [
       {
         "source": "/(.*)",
         "headers": [
           {"key": "X-Frame-Options", "value": "DENY"},
           {"key": "X-Content-Type-Options", "value": "nosniff"},
           {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"}
         ]
       }
     ],
     "routes": [
       {"src": "/login", "dest": "/login.html"},
       {"src": "/register", "dest": "/register.html"},
       {"src": "/dashboard", "dest": "/dashboard.html"},
       {"src": "/admin", "dest": "/admin.html"}
     ]
   }

2. backend/render.yaml  (for Render.com deployment)
   services:
   - type: web
     name: bulkreach-backend
     env: python
     buildCommand: pip install -r requirements.txt
     startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
     envVars: list all .env vars as references

3. Procfile (Railway/Heroku compatible)
   web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT --workers 2

4. backend/startup_check.py
   Pre-flight validation script (run manually before production deploy):
   - Test MongoDB connection and list collections
   - Verify admin user exists (seed if not)
   - Test Fernet encryption round-trip
   - Verify all 9 collections have correct indexes
   - Print: "✓ All checks passed. Ready to deploy."

5. backend/main.py (FINAL VERSION — update from Step 1)
   Ensure it includes:
   - lifespan with: init_db(), seed_admin(), start_scheduler(), create indexes
   - All 10 routers included with /api prefix
   - CORS from config.CORS_ORIGINS (split comma-separated string to list)
   - slowapi limiter with custom 429 handler (returns JSON not HTML)
   - Global exception handler for unhandled errors (log + return 500 JSON)
   - /health endpoint: GET /health → {status, env, db_connected, scheduler_running}

6. frontend/js/api.js (FINAL VERSION — update from Step 7)
   Add this constant at top:
   const API_BASE = '';  // empty = same origin (Vercel proxies /api → backend)
   Ensure all fetch calls use relative paths starting with /api/

7. README.md (full project README)
   Include:
   - Project description
   - Prerequisites (Python 3.11, MongoDB Atlas account, Gemini API key)
   - Local dev setup:
     cd backend && pip install -r requirements.txt
     cp .env.example .env  (fill in values)
     uvicorn main:app --reload
   - Get Fernet key: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   - Get JWT secret: python -c "import secrets; print(secrets.token_hex(32))"
   - Frontend: open frontend/index.html (or serve with: npx serve frontend)
   - Vercel deploy: vercel --prod (from frontend/ folder)
   - Backend deploy: push to GitHub → connect to Render, set env vars
   - MongoDB Atlas: whitelist all IPs (0.0.0.0/0) for cloud deploy
   - Default admin login: jiteshbawaskar05@gmail.com / Jitesh001@
   - Env vars table with description for each

8. PRODUCTION_CHECKLIST.md
   Complete checklist of:
   □ Change all default secrets in .env (JWT_SECRET_KEY, ENCRYPTION_KEY)
   □ MongoDB Atlas: enable IP allowlist for production backend IP only
   □ Set APP_ENV=production in backend .env
   □ Set CORS_ORIGINS to exact Vercel domain (no wildcards)
   □ Enable MongoDB Atlas backups
   □ Set up UptimeRobot to ping /health every 5 minutes
   □ Add Google reCAPTCHA to register form (optional)
   □ Test SMTP with real send before going live
   □ Test admin login at /login.html
   □ Verify /api/admin/* returns 403 for non-admin JWT
   □ Test CSV import with 100+ contacts
   □ Test Gemini AI compose
   □ Verify mail delay is minimum 60 seconds
   □ Test reply IMAP fetch
   □ Verify audit logs writing on key actions
   □ Load test with 10 concurrent users (optional)
   □ Set daily send limit in user settings before first campaign

9. PROJECT_STRUCTURE.md
   Complete file tree of every file in the project with one-line description.
   Format: path/to/file.ext → Description of what it does

Output every file fully. No truncation.
```

---

## Quick Reference: Build Order

| Step | What You Build | Key Outputs |
|------|---------------|-------------|
| 1 | Scaffold + Config + DB | main.py, database.py, all models, .env.example |
| 2 | Auth System | JWT, login/register routes, role guards |
| 3 | Settings + Contacts + Validation | SMTP/IMAP/AI settings, CSV/Sheets import |
| 4 | Mail Engine | Anti-spam sender, queue, pause/resume |
| 5 | AI + Templates + Schedules + Replies | Gemini compose, template CRUD, APScheduler |
| 6 | Admin Backend | All admin routes, live monitoring, user CRUD |
| 7 | Frontend Foundation | CSS design system, api.js, auth.js, landing page |
| 8 | User Dashboard | All 9 user pages (dashboard, bulk mail, history, etc.) |
| 9 | Admin Dashboard | All 6 admin pages (dark theme) |
| 10 | Deploy + Wiring | Vercel config, Render config, README, checklist |

## Tips for Best Gemini Output

- **Always paste the SYSTEM CONTEXT block** at the start of a new session
- **Complete one step fully** before starting the next
- If a file gets truncated, send: *"Continue from where you stopped. Output the rest of [filename] completely."*
- For Step 4 (mail engine), if output is cut: split into two requests — mail_service.py first, then scheduler_service.py + mail router
- Test backend after Steps 1–6 before building frontend (run `python startup_check.py`)