# BulkReach Pro

AI-powered cold email platform for agencies and teams. Send thousands of personalized emails daily with built-in warmup, reply tracking, and real-time analytics.

---

## What it does

- **Bulk email campaigns** — drip engine sends one-by-one with human-like delays to protect deliverability
- **AI personalization** — Google Gemini writes copy tailored to each prospect
- **Contact management** — import via CSV, paste emails, or sync from Google Sheets
- **Reply tracking** — IMAP sync auto-categorizes responses inside the dashboard
- **Multi-user** — every user has isolated SMTP credentials, campaigns, and contacts
- **Admin panel** — manage users, monitor live jobs, and impersonate accounts for support

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+ / FastAPI (async) |
| Database | MongoDB Atlas (Motor driver) |
| Auth | JWT (HS256) + Fernet-encrypted secrets |
| AI | Google Gemini via `google-generativeai` |
| Email | `aiosmtplib` (async SMTP) / `imaplib` |
| Scheduling | APScheduler 3.x |
| Frontend | Vanilla JS / HTML / CSS (no framework) |
| Deploy | Vercel (frontend static + backend Python) |

---

## Quick start (local)

### 1. Prerequisites

- Python 3.11+
- MongoDB Atlas account (free tier works fine)
- A Gmail / any SMTP account for sending

### 2. Install dependencies

```bash
git clone <your-repo>
cd mail_sender_app

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure `.env`

Copy the template and fill in your values:

```env
# MongoDB
MONGODB_URI=mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/
MONGODB_DB_NAME=bulkreach_prod

# JWT (generate: python -c "import secrets; print(secrets.token_hex(32))")
JWT_SECRET_KEY=your_64_char_hex_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7

# Fernet encryption key (generate: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
ENCRYPTION_KEY=your_fernet_key_here

# Admin account (created automatically on first boot)
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=StrongPassword123!
ADMIN_NAME=Your Name

# App
APP_ENV=development
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:8080
CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080

# Gemini AI (optional — users can also supply their own key in Settings)
GEMINI_API_KEY=

# Default SMTP (optional — lets you one-click apply SMTP in Settings → "Apply .env SMTP")
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_USE_TLS=true
SMTP_USE_SSL=false
SMTP_FROM_NAME=Your Name
SMTP_REPLY_TO=you@gmail.com
```

> **Gmail users**: use an [App Password](https://myaccount.google.com/apppasswords), not your real password. Enable 2FA first.

### 4. Run

```bash
# Terminal 1 — Backend API (port 8000)
python -m uvicorn backend.main:app --reload

# Terminal 2 — Frontend static server (port 8080)
python -m http.server 8080 --directory frontend
```

Open `http://localhost:8080` — the admin account is created automatically on first boot.

---

## Deploying to Vercel

The project is pre-configured. One command deploys both the frontend and API:

```bash
# Install Vercel CLI if you haven't
npm i -g vercel

# Deploy
vercel --prod
```

### Required environment variables in Vercel dashboard

Go to **Project → Settings → Environment Variables** and add every key from `.env` **except** `APP_ENV` (already set to `production` in `vercel.json`):

| Variable | Required | Notes |
|---|---|---|
| `MONGODB_URI` | ✅ | Atlas connection string |
| `JWT_SECRET_KEY` | ✅ | 64-char hex |
| `ENCRYPTION_KEY` | ✅ | Fernet key |
| `ADMIN_EMAIL` | ✅ | First admin account |
| `ADMIN_PASSWORD` | ✅ | Strong password |
| `CORS_ORIGINS` | ✅ | Your Vercel domain, e.g. `https://yourapp.vercel.app` |
| `GEMINI_API_KEY` | optional | Global AI fallback |
| `SMTP_*` | optional | One-click SMTP apply for admin |

> ⚠️ **APScheduler note**: Vercel runs serverless functions — background schedulers don't persist between requests. For production scheduling, use a cron trigger (e.g., Vercel Cron, Railway, or Render with a persistent process).

### Alternative: Render / Railway (recommended for scheduling)

These platforms run a persistent process so APScheduler works continuously:

```bash
# Render start command
uvicorn backend.main:app --host 0.0.0.0 --port $PORT

# Static frontend — deploy /frontend as a separate static site or serve from FastAPI
```

---

## User guide

### Sending your first campaign

1. **Settings → Sender Profiles** — add your SMTP account (or click "Apply .env SMTP" if configured)
2. **Contacts** — create a list and import contacts via CSV or paste
3. **Templates** — create an HTML email template with merge tags (`{name}`, `{org}`)
4. **Bulk Mail** — select template + contact list, set delay (min 60s) and daily limit, then send

### SMTP setup (Gmail)

1. Enable [2-Step Verification](https://myaccount.google.com/security)
2. Generate an [App Password](https://myaccount.google.com/apppasswords) for "Mail"
3. Use `smtp.gmail.com`, port `587`, STARTTLS enabled
4. Use the App Password — not your Google account password

### Merge tags in templates

| Tag | Replaced with |
|---|---|
| `{name}` | Contact's name |
| `{org}` | Contact's organization |
| `{email}` | Contact's email address |
| `{first_name}` | First word of name |

### Contact import formats

**CSV** — columns: `email` (required), `name` (optional), `org` (optional)

```csv
email,name,org
alice@example.com,Alice Smith,Acme Corp
bob@startup.io,Bob Jones,Startup Inc
```

**Paste** — one email per line, or `name, email` per line

```
alice@example.com
Bob Jones, bob@startup.io
```

---

## Project structure

```
mail_sender_app/
├── backend/
│   ├── main.py              # FastAPI app, CORS, lifespan
│   ├── config.py            # All settings via pydantic-settings
│   ├── database.py          # MongoDB connection, init, seed
│   ├── middleware/
│   │   ├── auth_middleware.py
│   │   └── audit_middleware.py
│   ├── routers/             # One file per feature domain
│   │   ├── auth.py
│   │   ├── contacts.py
│   │   ├── mail.py
│   │   ├── settings.py
│   │   ├── template.py
│   │   ├── schedule.py
│   │   ├── replies.py
│   │   ├── ai.py
│   │   ├── user.py
│   │   └── admin.py
│   ├── services/            # Business logic
│   ├── models/              # Pydantic models
│   └── utils/
│       └── helpers.py       # encrypt/decrypt, json_safe
├── frontend/
│   ├── index.html           # Landing page
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── admin.html
│   ├── pages/               # All authenticated app pages
│   ├── css/
│   └── js/
│       ├── api.js           # Fetch wrapper, token management
│       ├── auth.js          # Login/register forms
│       └── sidebar.js       # User info, logout, admin link
├── requirements.txt
├── vercel.json
└── .env                     # Never commit this
```

---

## Security notes

- All SMTP passwords, IMAP passwords, and API keys are **Fernet-encrypted** before storage
- JWT access tokens expire in 24h; refresh tokens in 7 days
- Every database query is scoped to `user_id` — users cannot access each other's data
- Admin routes require `role = admin` in the JWT payload
- Rate limiting via `slowapi` on auth endpoints
- Passwords hashed with `bcrypt`

---

## License

Built for internal use. Contact the maintainer for licensing.
