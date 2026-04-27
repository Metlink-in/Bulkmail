# 🚀 BulkReach Pro

**The Ultimate Multi-Tenant Cold Email Engine for Modern Agencies.**

BulkReach Pro is a production-grade cold outreach SaaS platform designed for massive scalability, high deliverability, and AI-driven personalization. Built with a high-performance FastAPI backend and a premium, responsive UI.

---

## ✨ Key Features

### 👤 User Capabilities
*   **AI Smart Compose**: Generate high-converting email copy using Google Gemini AI.
*   **Multi-Source Import**: Seamlessly import contacts via **CSV** or direct **Google Sheets** integration.
*   **Dynamic Personalization**: Use liquid-style tokens (`{first_name}`, `{company}`) for unique messaging at scale.
*   **Inbox Sync**: Track replies directly from your IMAP server within the dashboard.
*   **Recurring Automation**: Schedule campaigns once or set them on a recurring cron schedule (Daily/Weekly).
*   **Global Settings**: Securely store SMTP, IMAP, and AI credentials with hardware-grade encryption.

### 🛡️ Admin Command Center
*   **Live Monitoring**: Real-time visibility into all active mail jobs across the entire platform.
*   **User Management**: Full CRUD operations on user accounts, including deactivation and hard deletion.
*   **Secure Impersonation**: Admins can securely impersonate user accounts for troubleshooting or white-glove setup.
*   **System-Wide Auditing**: Comprehensive logs tracking every critical action performed on the platform.

---

## 🛠️ Technical Stack

*   **Backend**: Python 3.14+ / FastAPI (Asynchronous ASGI)
*   **Database**: MongoDB (Motor Driver)
*   **Task Scheduling**: APScheduler (Persistent & Distributed ready)
*   **Security**: JWT (HS256), Fernet (AES-128 Encryption), BCrypt Hashing
*   **AI**: Google Generative AI (Gemini)
*   **Frontend**: Premium Vanilla JS / CSS3 / HTML5

---

## 🚦 Quick Start

### 1. Prerequisites
*   Python 3.11 or higher
*   A MongoDB Atlas connection string
*   Google Gemini API Key (optional but recommended)

### 2. Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd mail_sender_app

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory (refer to `.env.example`):
```env
MONGODB_URI=mongodb+srv://...
MONGODB_DB_NAME=bulkreach_prod
JWT_SECRET_KEY=your_64_char_hex
ENCRYPTION_KEY=your_fernet_key
```

### 4. Run the Application
```bash
# Start Backend (Port 8000)
python -m uvicorn backend.main:app --reload

# Start Frontend (Port 3000)
python -m http.server 3000 --directory frontend
```

---

## 🔐 Default Credentials (Admin)
*   **Email**: `jiteshbawaskar05@gmail.com`
*   **Password**: `Jitesh001@`

---

## 🌍 Deployment

### Vercel (Recommended)
This project is pre-configured for Vercel. The `vercel.json` handles routing and environment mapping automatically.
```bash
vercel --prod
```

### PaaS (Render/Railway)
Use the included `Procfile` and `render.yaml` for zero-config deployment on most cloud platforms.

---

## 📝 License
Built with ❤️ for BulkReach Agencies.
