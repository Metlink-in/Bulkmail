# Production Deployment Checklist

### Security & Secrets
- [ ] Change all default secrets in `.env` (`JWT_SECRET_KEY`, `ENCRYPTION_KEY`)
- [ ] Set `APP_ENV=production` in backend `.env`
- [ ] Set `CORS_ORIGINS` to exact Vercel domain (no wildcards `*`)
- [ ] Add Google reCAPTCHA to register form (optional)

### Database Infrastructure
- [ ] MongoDB Atlas: Enable IP allowlist strictly for production backend IP (avoid 0.0.0.0/0 if using static IPs)
- [ ] Enable MongoDB Atlas automated backups
- [ ] Execute `python backend/startup_check.py` to validate production connectivity

### Monitoring & Validation
- [ ] Set up UptimeRobot to ping `/health` every 5 minutes
- [ ] Test SMTP with a live test campaign before soft launching
- [ ] Test Admin login at `/login.html` and verify telemetry dashboard works
- [ ] Verify `/api/admin/*` endpoints explicitly return `403` for non-admin JWTs
- [ ] Test CSV import with 100+ contacts natively
- [ ] Test Gemini AI Compose block
- [ ] Verify background mail delay respects the minimum 60-second limit
- [ ] Test IMAP Fetch functionality with live replies
- [ ] Verify Audit Logs write on security mutations (`login`, `crud`, etc.)

### Scaling
- [ ] Load test the platform with 10 concurrent users (optional)
- [ ] Set daily send limits in user settings prior to first campaign launch
