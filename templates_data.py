"""
Global starter email templates.
All CSS is inline for Gmail / Outlook / Apple Mail compatibility.
Merge tags: {first_name}  {org}  {email}

Gmail strips linear-gradient — every coloured <td> now carries:
  bgcolor="#HEX"              (HTML4 attribute, always respected)
  background-color:#HEX;     (CSS fallback before the gradient)
  background:linear-gradient(...);  (for modern clients)
"""

GLOBAL_TEMPLATES = [

    # ── 1. Metlink Outreach — Purple ───────────────────────────────────────
    {
        "name": "Metlink Outreach",
        "subject": "Quick question for {first_name} at {org}",
        "html_body": """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:20px 0;background-color:#f4f7fb;font-family:Arial,sans-serif;">
<table align="center" width="600" cellpadding="0" cellspacing="0" bgcolor="#ffffff" style="max-width:600px;width:100%;background-color:#ffffff;">

  <!-- HEADER -->
  <tr>
    <td bgcolor="#4A00E0" style="background-color:#4A00E0;background:linear-gradient(135deg,#4A00E0 0%,#8E2DE2 100%);padding:36px 40px;text-align:center;">
      <h1 style="margin:0;font-size:28px;font-weight:800;color:#ffffff;letter-spacing:-0.5px;">Metlink</h1>
      <p style="margin:6px 0 0;font-size:13px;color:rgba(255,255,255,0.80);letter-spacing:0.5px;">Smart Solutions. Real Growth.</p>
    </td>
  </tr>

  <!-- BODY -->
  <tr>
    <td bgcolor="#ffffff" style="background-color:#ffffff;padding:36px 40px;">
      <h2 style="margin:0 0 20px;font-size:22px;color:#4A00E0;font-weight:700;">Let's Help You Scale Faster 🚀</h2>

      <p style="margin:0 0 16px;font-size:15px;line-height:1.7;color:#1f2937;">Hi <strong>{first_name}</strong>,</p>

      <p style="margin:0 0 16px;font-size:15px;line-height:1.7;color:#374151;">
        I came across your work at <strong style="color:#4A00E0;">{org}</strong> and was impressed by what you're building.
      </p>

      <p style="margin:0 0 20px;font-size:15px;line-height:1.7;color:#374151;">
        At <strong>Metlink</strong>, we help businesses streamline operations, automate workflows, and unlock scalable growth using modern tech and AI-driven systems.
      </p>

      <!-- HIGHLIGHT BOX — bgcolor required; Gmail strips background: shorthand from <td> -->
      <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 24px;">
        <tr>
          <td bgcolor="#f3f0ff" style="background-color:#f3f0ff;border-left:4px solid #8E2DE2;padding:18px 20px;">
            <p style="margin:0 0 10px;font-size:14px;font-weight:700;color:#4A00E0;">⚡ What we can help with:</p>
            <p style="margin:0 0 6px;font-size:14px;color:#374151;line-height:1.6;">• Automation &amp; AI integration</p>
            <p style="margin:0 0 6px;font-size:14px;color:#374151;line-height:1.6;">• Custom web &amp; backend systems</p>
            <p style="margin:0;font-size:14px;color:#374151;line-height:1.6;">• Growth-focused digital solutions</p>
          </td>
        </tr>
      </table>

      <p style="margin:0 0 28px;font-size:15px;line-height:1.7;color:#374151;">
        Would you be open to a quick 15-minute chat to explore if this aligns with your current goals?
      </p>

      <!-- CTA — solid background-color only; Gmail strips linear-gradient from <a> tags -->
      <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 28px;">
        <tr>
          <td align="center">
            <a href="#" style="display:inline-block;background-color:#4A00E0;color:#ffffff;font-size:15px;font-weight:700;text-decoration:none;padding:14px 36px;border-radius:8px;">Book a Quick Call →</a>
          </td>
        </tr>
      </table>

      <p style="margin:0;font-size:14px;color:#6b7280;line-height:1.7;">
        Looking forward to connecting,<br>
        <strong style="color:#1f2937;">{sender_name}</strong>
      </p>
    </td>
  </tr>

  <!-- FOOTER -->
  <tr>
    <td bgcolor="#f9f5ff" style="background-color:#f9f5ff;padding:16px 40px;text-align:center;border-top:1px solid #ede9fe;">
      <p style="margin:0;font-size:12px;color:#9ca3af;">© 2026 Metlink · All rights reserved</p>
      <p style="margin:4px 0 0;font-size:12px;"><a href="#" style="color:#8E2DE2;text-decoration:none;">Unsubscribe</a></p>
    </td>
  </tr>

</table>
</body>
</html>""",
    },

    # ── 2. Cold B2B Intro — Blue ───────────────────────────────────────────
    {
        "name": "Cold B2B Intro — Blue",
        "subject": "Had a quick idea for {org}, {first_name}",
        "html_body": """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:20px 0;background:#eef2f7;font-family:Arial,sans-serif;">
<table align="center" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.09);">

  <!-- HEADER -->
  <tr>
    <td bgcolor="#1e3a8a" style="background-color:#1e3a8a;background:linear-gradient(135deg,#1e3a8a 0%,#2563eb 100%);padding:40px;text-align:center;">
      <div style="font-size:42px;margin-bottom:12px;">🎯</div>
      <h1 style="margin:0;font-size:24px;font-weight:800;color:#fff;">Hi {first_name} — got a minute?</h1>
      <p style="margin:8px 0 0;font-size:13px;color:rgba(255,255,255,0.75);">A short note worth your time</p>
    </td>
  </tr>

  <!-- BODY -->
  <tr>
    <td style="padding:36px 40px;">
      <p style="margin:0 0 16px;font-size:15px;line-height:1.7;color:#1f2937;">
        I was researching <strong style="color:#2563eb;">{org}</strong> and was genuinely impressed — it's rare to see this level of execution.
      </p>
      <p style="margin:0 0 20px;font-size:15px;line-height:1.7;color:#374151;">
        We help B2B teams <strong>increase qualified replies by 40%</strong> in under 60 days through AI-personalized outreach — without burning domain reputation or adding manual work.
      </p>

      <!-- BENEFITS -->
      <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 24px;background:#eff6ff;border-radius:10px;overflow:hidden;">
        <tr>
          <td style="padding:20px 24px;">
            <p style="margin:0 0 12px;font-size:14px;font-weight:700;color:#1e40af;">What teams like {org} get:</p>
            <p style="margin:0 0 8px;font-size:14px;color:#374151;line-height:1.6;">✅ &nbsp;Personalized cold email at scale</p>
            <p style="margin:0 0 8px;font-size:14px;color:#374151;line-height:1.6;">✅ &nbsp;Auto reply tracking &amp; inbox sync</p>
            <p style="margin:0;font-size:14px;color:#374151;line-height:1.6;">✅ &nbsp;Deliverability protection built-in</p>
          </td>
        </tr>
      </table>

      <p style="margin:0 0 28px;font-size:15px;line-height:1.7;color:#374151;">
        Worth a quick 15-minute call to see if there's a fit?
      </p>

      <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 28px;">
        <tr>
          <td align="center">
            <a href="#" style="display:inline-block;background-color:#1e3a8a;background:linear-gradient(135deg,#1e3a8a,#2563eb);color:#fff;font-size:15px;font-weight:700;text-decoration:none;padding:14px 36px;border-radius:8px;">Book a Free 15-Min Call →</a>
          </td>
        </tr>
      </table>

      <p style="margin:0;font-size:14px;color:#6b7280;line-height:1.7;">
        Best,<br><strong style="color:#1f2937;">{sender_name}</strong><br>
        <span style="font-size:13px;color:#9ca3af;">{sender_email}</span>
      </p>
    </td>
  </tr>

  <!-- FOOTER -->
  <tr>
    <td style="background:#f0f4ff;padding:16px 40px;text-align:center;border-top:1px solid #dbeafe;">
      <p style="margin:0;font-size:12px;color:#9ca3af;">You received this because of your work at {org}.</p>
      <p style="margin:4px 0 0;font-size:12px;"><a href="#" style="color:#2563eb;text-decoration:none;">Unsubscribe</a></p>
    </td>
  </tr>

</table>
</body>
</html>""",
    },

    # ── 3. Follow-Up — Orange ──────────────────────────────────────────────
    {
        "name": "Follow-Up Email — Orange",
        "subject": "Following up, {first_name}",
        "html_body": """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:20px 0;background:#fff7ed;font-family:Arial,sans-serif;">
<table align="center" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.09);">

  <!-- HEADER -->
  <tr>
    <td bgcolor="#c2410c" style="background-color:#c2410c;background:linear-gradient(135deg,#c2410c 0%,#ea580c 100%);padding:36px 40px;text-align:center;">
      <div style="font-size:40px;margin-bottom:12px;">👋</div>
      <h1 style="margin:0;font-size:24px;font-weight:800;color:#fff;">Just Checking In</h1>
      <p style="margin:8px 0 0;font-size:13px;color:rgba(255,255,255,0.80);">Still thinking it over? No pressure.</p>
    </td>
  </tr>

  <!-- BODY -->
  <tr>
    <td style="padding:36px 40px;">
      <p style="margin:0 0 16px;font-size:15px;line-height:1.7;color:#1f2937;">Hi <strong>{first_name}</strong>,</p>

      <p style="margin:0 0 16px;font-size:15px;line-height:1.7;color:#374151;">
        I sent you a note last week about how we've been helping teams at companies like <strong>{org}</strong> — just wanted to bump it to the top of your inbox in case life got busy.
      </p>

      <p style="margin:0 0 20px;font-size:15px;line-height:1.7;color:#374151;">
        In short: we help B2B teams <strong>reduce outreach time by 60%</strong> while increasing response rates. Even if now isn't the right time, I'd love to hear your thoughts.
      </p>

      <!-- REMINDER BOX -->
      <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 24px;">
        <tr>
          <td style="background:#fff7ed;border:1px solid #fed7aa;border-radius:10px;padding:18px 22px;">
            <p style="margin:0;font-size:14px;color:#9a3412;font-weight:700;">🔁 Quick recap of what I offered:</p>
            <p style="margin:8px 0 0;font-size:14px;color:#374151;line-height:1.7;">
              A free 15-minute strategy call where we'll map out exactly how our system would work for <strong>{org}</strong> — zero sales pressure, just value.
            </p>
          </td>
        </tr>
      </table>

      <p style="margin:0 0 28px;font-size:15px;line-height:1.7;color:#374151;">
        If you're interested, simply reply to this email or pick a time below. If now's not the right time, I completely understand — just say the word and I'll stop following up.
      </p>

      <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 28px;">
        <tr>
          <td align="center">
            <a href="#" style="display:inline-block;background-color:#c2410c;background:linear-gradient(135deg,#c2410c,#ea580c);color:#fff;font-size:15px;font-weight:700;text-decoration:none;padding:14px 36px;border-radius:8px;">Pick a Time →</a>
          </td>
        </tr>
      </table>

      <p style="margin:0;font-size:14px;color:#6b7280;line-height:1.7;">
        Cheers,<br><strong style="color:#1f2937;">{sender_name}</strong><br>
        <span style="font-size:13px;color:#9ca3af;">{sender_email}</span>
      </p>
    </td>
  </tr>

  <!-- FOOTER -->
  <tr>
    <td style="background:#fff7ed;padding:16px 40px;text-align:center;border-top:1px solid #fed7aa;">
      <p style="margin:0;font-size:12px;color:#9ca3af;">You received this as a follow-up to a previous note.</p>
      <p style="margin:4px 0 0;font-size:12px;"><a href="#" style="color:#ea580c;text-decoration:none;">Unsubscribe</a></p>
    </td>
  </tr>

</table>
</body>
</html>""",
    },

    # ── 4. SaaS Demo Invite — Teal ─────────────────────────────────────────
    {
        "name": "SaaS Demo Invite — Teal",
        "subject": "See exactly how we'd help {org}, {first_name}",
        "html_body": """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:20px 0;background:#f0fdf4;font-family:Arial,sans-serif;">
<table align="center" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.09);">

  <!-- HEADER -->
  <tr>
    <td bgcolor="#065f46" style="background-color:#065f46;background:linear-gradient(135deg,#065f46 0%,#059669 100%);padding:40px;text-align:center;">
      <div style="font-size:42px;margin-bottom:12px;">🖥️</div>
      <h1 style="margin:0;font-size:24px;font-weight:800;color:#fff;">See It in Action</h1>
      <p style="margin:8px 0 0;font-size:13px;color:rgba(255,255,255,0.80);">A personalised demo built for {org}</p>
    </td>
  </tr>

  <!-- BODY -->
  <tr>
    <td style="padding:36px 40px;">
      <p style="margin:0 0 16px;font-size:15px;line-height:1.7;color:#1f2937;">Hi <strong>{first_name}</strong>,</p>

      <p style="margin:0 0 16px;font-size:15px;line-height:1.7;color:#374151;">
        I've put together a short personalised demo showing exactly how our platform would work for a team like <strong style="color:#059669;">{org}</strong>.
      </p>

      <p style="margin:0 0 20px;font-size:15px;line-height:1.7;color:#374151;">
        No generic slides — just a real walkthrough of your specific use case in under 20 minutes.
      </p>

      <!-- STATS ROW -->
      <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 24px;">
        <tr>
          <td width="32%" style="background:#ecfdf5;border-radius:8px;padding:16px;text-align:center;">
            <p style="margin:0;font-size:24px;font-weight:800;color:#065f46;">3×</p>
            <p style="margin:4px 0 0;font-size:12px;color:#374151;">Faster onboarding</p>
          </td>
          <td width="4%"></td>
          <td width="32%" style="background:#ecfdf5;border-radius:8px;padding:16px;text-align:center;">
            <p style="margin:0;font-size:24px;font-weight:800;color:#065f46;">60%</p>
            <p style="margin:4px 0 0;font-size:12px;color:#374151;">Less manual work</p>
          </td>
          <td width="4%"></td>
          <td width="28%" style="background:#ecfdf5;border-radius:8px;padding:16px;text-align:center;">
            <p style="margin:0;font-size:24px;font-weight:800;color:#065f46;">40%</p>
            <p style="margin:4px 0 0;font-size:12px;color:#374151;">More replies</p>
          </td>
        </tr>
      </table>

      <p style="margin:0 0 28px;font-size:15px;line-height:1.7;color:#374151;">
        I have a few slots open this week. Want to grab one?
      </p>

      <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 28px;">
        <tr>
          <td align="center">
            <a href="#" style="display:inline-block;background-color:#065f46;background:linear-gradient(135deg,#065f46,#059669);color:#fff;font-size:15px;font-weight:700;text-decoration:none;padding:14px 36px;border-radius:8px;">Book My Demo Slot →</a>
          </td>
        </tr>
      </table>

      <p style="margin:0;font-size:14px;color:#6b7280;line-height:1.7;">
        Talk soon,<br><strong style="color:#1f2937;">{sender_name}</strong><br>
        <span style="font-size:13px;color:#9ca3af;">{sender_email}</span>
      </p>
    </td>
  </tr>

  <!-- FOOTER -->
  <tr>
    <td style="background:#f0fdf4;padding:16px 40px;text-align:center;border-top:1px solid #bbf7d0;">
      <p style="margin:0;font-size:12px;color:#9ca3af;">Sent to {first_name} at {org}</p>
      <p style="margin:4px 0 0;font-size:12px;"><a href="#" style="color:#059669;text-decoration:none;">Unsubscribe</a></p>
    </td>
  </tr>

</table>
</body>
</html>""",
    },

    # ── 5. Newsletter — Dark Blue ──────────────────────────────────────────
    {
        "name": "Newsletter — Dark Blue",
        "subject": "📬 This month at {org} — our latest updates",
        "html_body": """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:20px 0;background:#f1f5f9;font-family:Arial,sans-serif;">
<table align="center" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.09);">

  <!-- HEADER -->
  <tr>
    <td bgcolor="#0f172a" style="background-color:#0f172a;background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 100%);padding:36px 40px;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td>
            <p style="margin:0;font-size:12px;color:#94a3b8;letter-spacing:1px;text-transform:uppercase;">Monthly Update</p>
            <h1 style="margin:6px 0 0;font-size:26px;font-weight:800;color:#fff;">Your Newsletter</h1>
          </td>
          <td align="right">
            <p style="margin:0;font-size:13px;color:#64748b;">May 2026</p>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- GREETING -->
  <tr>
    <td style="padding:28px 40px 0;">
      <p style="margin:0 0 16px;font-size:15px;line-height:1.7;color:#374151;">Hi <strong>{first_name}</strong>,</p>
      <p style="margin:0 0 24px;font-size:15px;line-height:1.7;color:#374151;">Here's what's been happening this month — tips, updates, and resources we think you'll love.</p>
      <hr style="border:none;border-top:1px solid #e2e8f0;margin:0 0 24px;">
    </td>
  </tr>

  <!-- ARTICLE 1 -->
  <tr>
    <td style="padding:0 40px 24px;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc;border-radius:10px;overflow:hidden;">
        <tr>
          <td style="background:#3b82f6;width:4px;"></td>
          <td style="padding:20px 20px 20px 16px;">
            <p style="margin:0 0 4px;font-size:11px;color:#3b82f6;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;">Feature Update</p>
            <h3 style="margin:0 0 8px;font-size:17px;color:#0f172a;">New automation workflows are live 🎉</h3>
            <p style="margin:0;font-size:14px;color:#475569;line-height:1.6;">We've just shipped multi-step automation — build powerful sequences in minutes with no code required.</p>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- ARTICLE 2 -->
  <tr>
    <td style="padding:0 40px 24px;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc;border-radius:10px;overflow:hidden;">
        <tr>
          <td style="background:#8b5cf6;width:4px;"></td>
          <td style="padding:20px 20px 20px 16px;">
            <p style="margin:0 0 4px;font-size:11px;color:#8b5cf6;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;">Tip of the Month</p>
            <h3 style="margin:0 0 8px;font-size:17px;color:#0f172a;">How to get 50% more opens 📈</h3>
            <p style="margin:0;font-size:14px;color:#475569;line-height:1.6;">Personalise the first line of every email with something specific to the recipient — we've seen open rates jump dramatically.</p>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- ARTICLE 3 -->
  <tr>
    <td style="padding:0 40px 24px;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc;border-radius:10px;overflow:hidden;">
        <tr>
          <td style="background:#10b981;width:4px;"></td>
          <td style="padding:20px 20px 20px 16px;">
            <p style="margin:0 0 4px;font-size:11px;color:#10b981;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;">Case Study</p>
            <h3 style="margin:0 0 8px;font-size:17px;color:#0f172a;">How Acme Corp closed 12 deals in 30 days</h3>
            <p style="margin:0;font-size:14px;color:#475569;line-height:1.6;">Read how one team used our platform to build a repeatable outbound system from scratch.</p>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- CTA -->
  <tr>
    <td style="padding:4px 40px 32px;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td align="center">
            <a href="#" style="display:inline-block;background-color:#0f172a;background:linear-gradient(135deg,#0f172a,#1e3a5f);color:#fff;font-size:15px;font-weight:700;text-decoration:none;padding:14px 36px;border-radius:8px;">Read All Updates →</a>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- FOOTER -->
  <tr>
    <td style="background:#f1f5f9;padding:20px 40px;text-align:center;border-top:1px solid #e2e8f0;">
      <p style="margin:0;font-size:12px;color:#94a3b8;">You're receiving this because you subscribed as <strong>{first_name}</strong> at <strong>{org}</strong>.</p>
      <p style="margin:6px 0 0;font-size:12px;"><a href="#" style="color:#3b82f6;text-decoration:none;">Unsubscribe</a> &nbsp;·&nbsp; <a href="#" style="color:#3b82f6;text-decoration:none;">View in browser</a></p>
    </td>
  </tr>

</table>
</body>
</html>""",
    },

    # ── 6. Webinar / Event Invite — Red ────────────────────────────────────
    {
        "name": "Webinar Invitation — Red",
        "subject": "🎙️ You're invited, {first_name} — free live workshop",
        "html_body": """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:20px 0;background:#fff1f2;font-family:Arial,sans-serif;">
<table align="center" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.09);">

  <!-- HEADER -->
  <tr>
    <td bgcolor="#9f1239" style="background-color:#9f1239;background:linear-gradient(135deg,#9f1239 0%,#e11d48 100%);padding:40px;text-align:center;">
      <p style="margin:0;font-size:12px;color:rgba(255,255,255,0.70);letter-spacing:1.5px;text-transform:uppercase;font-weight:600;">Free Live Workshop</p>
      <h1 style="margin:10px 0;font-size:26px;font-weight:800;color:#fff;line-height:1.3;">Grow Your Pipeline by 3× in 60 Days</h1>
      <table align="center" cellpadding="0" cellspacing="0" style="margin-top:16px;">
        <tr>
          <td style="background:rgba(255,255,255,0.15);border-radius:6px;padding:8px 16px;text-align:center;">
            <p style="margin:0;font-size:14px;color:#fff;font-weight:600;">📅 Thursday, May 15 · 11:00 AM IST</p>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- BODY -->
  <tr>
    <td style="padding:36px 40px;">
      <p style="margin:0 0 16px;font-size:15px;line-height:1.7;color:#1f2937;">Hi <strong>{first_name}</strong>,</p>

      <p style="margin:0 0 16px;font-size:15px;line-height:1.7;color:#374151;">
        You're personally invited to our free live workshop — built specifically for leaders like you at <strong style="color:#e11d48;">{org}</strong>.
      </p>

      <p style="margin:0 0 20px;font-size:15px;font-weight:700;color:#0f172a;">In 60 minutes you'll learn:</p>

      <!-- AGENDA -->
      <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 24px;">
        <tr>
          <td style="padding:10px 0;border-bottom:1px solid #f1f5f9;">
            <p style="margin:0;font-size:14px;color:#374151;line-height:1.6;">🔴 &nbsp;<strong>How to build a repeatable outbound system</strong> that works while you sleep</p>
          </td>
        </tr>
        <tr>
          <td style="padding:10px 0;border-bottom:1px solid #f1f5f9;">
            <p style="margin:0;font-size:14px;color:#374151;line-height:1.6;">🔴 &nbsp;<strong>The exact email frameworks</strong> getting 40%+ reply rates right now</p>
          </td>
        </tr>
        <tr>
          <td style="padding:10px 0;">
            <p style="margin:0;font-size:14px;color:#374151;line-height:1.6;">🔴 &nbsp;<strong>Live Q&amp;A</strong> — bring your toughest outreach challenges</p>
          </td>
        </tr>
      </table>

      <!-- URGENCY -->
      <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 24px;">
        <tr>
          <td style="background:#fff1f2;border:1px solid #fecdd3;border-radius:8px;padding:14px 18px;text-align:center;">
            <p style="margin:0;font-size:14px;color:#9f1239;font-weight:700;">⚠️ Limited seats — only 50 spots available.</p>
          </td>
        </tr>
      </table>

      <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 28px;">
        <tr>
          <td align="center">
            <a href="#" style="display:inline-block;background-color:#9f1239;background:linear-gradient(135deg,#9f1239,#e11d48);color:#fff;font-size:15px;font-weight:700;text-decoration:none;padding:14px 36px;border-radius:8px;">Reserve My Free Seat →</a>
          </td>
        </tr>
      </table>

      <p style="margin:0;font-size:14px;color:#6b7280;line-height:1.7;">
        See you there,<br><strong style="color:#1f2937;">{sender_name}</strong><br>
        <span style="font-size:13px;color:#9ca3af;">{sender_email}</span>
      </p>
    </td>
  </tr>

  <!-- FOOTER -->
  <tr>
    <td style="background:#fff1f2;padding:16px 40px;text-align:center;border-top:1px solid #fecdd3;">
      <p style="margin:0;font-size:12px;color:#9ca3af;">You were invited because of your role at {org}.</p>
      <p style="margin:4px 0 0;font-size:12px;"><a href="#" style="color:#e11d48;text-decoration:none;">Unsubscribe</a></p>
    </td>
  </tr>

</table>
</body>
</html>""",
    },

    # ── 7. Win-Back / Re-engagement — Amber ───────────────────────────────
    {
        "name": "Re-engagement — Amber",
        "subject": "We miss you, {first_name} 👋",
        "html_body": """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:20px 0;background:#fffbeb;font-family:Arial,sans-serif;">
<table align="center" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.09);">

  <!-- HEADER -->
  <tr>
    <td bgcolor="#b45309" style="background-color:#b45309;background:linear-gradient(135deg,#b45309 0%,#d97706 100%);padding:40px;text-align:center;">
      <div style="font-size:48px;margin-bottom:12px;">😢</div>
      <h1 style="margin:0;font-size:24px;font-weight:800;color:#fff;">We've Missed You, {first_name}</h1>
      <p style="margin:8px 0 0;font-size:13px;color:rgba(255,255,255,0.80);">It's been a while — let's reconnect</p>
    </td>
  </tr>

  <!-- BODY -->
  <tr>
    <td style="padding:36px 40px;">
      <p style="margin:0 0 16px;font-size:15px;line-height:1.7;color:#1f2937;">
        Hi <strong>{first_name}</strong>, we noticed you haven't been around for a while and we wanted to check in.
      </p>

      <p style="margin:0 0 20px;font-size:15px;line-height:1.7;color:#374151;">
        We've been busy building new features and improvements we know you'll love — and we don't want you to miss them.
      </p>

      <!-- WHAT'S NEW -->
      <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 24px;background:#fffbeb;border:1px solid #fde68a;border-radius:10px;">
        <tr>
          <td style="padding:20px 22px;">
            <p style="margin:0 0 12px;font-size:14px;font-weight:700;color:#b45309;">🆕 What's new since you left:</p>
            <p style="margin:0 0 8px;font-size:14px;color:#374151;line-height:1.6;">⚡ Faster automation builder — 3× quicker to set up</p>
            <p style="margin:0 0 8px;font-size:14px;color:#374151;line-height:1.6;">📊 Advanced analytics dashboard</p>
            <p style="margin:0;font-size:14px;color:#374151;line-height:1.6;">🤖 AI-powered email personalisation</p>
          </td>
        </tr>
      </table>

      <!-- OFFER -->
      <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 28px;">
        <tr>
          <td bgcolor="#b45309" align="center" style="background-color:#b45309;background:linear-gradient(135deg,#b45309,#d97706);border-radius:10px;padding:20px;">
            <p style="margin:0 0 4px;font-size:13px;color:rgba(255,255,255,0.80);">Special offer for returning users</p>
            <p style="margin:0;font-size:22px;font-weight:800;color:#fff;">30% OFF — This Week Only</p>
          </td>
        </tr>
      </table>

      <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 28px;">
        <tr>
          <td align="center">
            <a href="#" style="display:inline-block;background-color:#b45309;background:linear-gradient(135deg,#b45309,#d97706);color:#fff;font-size:15px;font-weight:700;text-decoration:none;padding:14px 36px;border-radius:8px;">Come Back &amp; Claim Offer →</a>
          </td>
        </tr>
      </table>

      <p style="margin:0;font-size:14px;color:#6b7280;line-height:1.7;">
        Hope to see you soon,<br><strong style="color:#1f2937;">{sender_name}</strong><br>
        <span style="font-size:13px;color:#9ca3af;">{sender_email}</span>
      </p>
    </td>
  </tr>

  <!-- FOOTER -->
  <tr>
    <td style="background:#fffbeb;padding:16px 40px;text-align:center;border-top:1px solid #fde68a;">
      <p style="margin:0;font-size:12px;color:#9ca3af;">You're receiving this because you previously signed up.</p>
      <p style="margin:4px 0 0;font-size:12px;"><a href="#" style="color:#d97706;text-decoration:none;">Unsubscribe</a></p>
    </td>
  </tr>

</table>
</body>
</html>""",
    },

    # ── 8. Thank You / Post-Meeting — Green ───────────────────────────────
    {
        "name": "Thank You — Post Meeting",
        "subject": "Great connecting with you, {first_name}!",
        "html_body": """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:20px 0;background:#f0fdf4;font-family:Arial,sans-serif;">
<table align="center" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.09);">

  <!-- HEADER -->
  <tr>
    <td bgcolor="#14532d" style="background-color:#14532d;background:linear-gradient(135deg,#14532d 0%,#16a34a 100%);padding:40px;text-align:center;">
      <div style="font-size:48px;margin-bottom:12px;">🤝</div>
      <h1 style="margin:0;font-size:24px;font-weight:800;color:#fff;">Thanks for Your Time!</h1>
      <p style="margin:8px 0 0;font-size:13px;color:rgba(255,255,255,0.80);">It was great connecting with you</p>
    </td>
  </tr>

  <!-- BODY -->
  <tr>
    <td style="padding:36px 40px;">
      <p style="margin:0 0 16px;font-size:15px;line-height:1.7;color:#1f2937;">Hi <strong>{first_name}</strong>,</p>

      <p style="margin:0 0 16px;font-size:15px;line-height:1.7;color:#374151;">
        Thank you so much for taking the time to speak with us. It was genuinely great learning more about <strong style="color:#16a34a;">{org}</strong> and the challenges you're working through.
      </p>

      <!-- RECAP -->
      <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 24px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;">
        <tr>
          <td style="padding:20px 22px;">
            <p style="margin:0 0 12px;font-size:14px;font-weight:700;color:#14532d;">📋 Quick recap from our conversation:</p>
            <p style="margin:0 0 8px;font-size:14px;color:#374151;line-height:1.6;">✅ &nbsp;Discussed your current workflow pain points</p>
            <p style="margin:0 0 8px;font-size:14px;color:#374151;line-height:1.6;">✅ &nbsp;Explored how automation can save 10+ hrs/week</p>
            <p style="margin:0;font-size:14px;color:#374151;line-height:1.6;">✅ &nbsp;Agreed to follow up with a custom proposal</p>
          </td>
        </tr>
      </table>

      <p style="margin:0 0 16px;font-size:15px;line-height:1.7;color:#374151;">
        As discussed, I'll send over a tailored proposal by end of this week. In the meantime, here are a couple of resources that might be helpful:
      </p>

      <!-- RESOURCES -->
      <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 24px;">
        <tr>
          <td style="padding:8px 0;border-bottom:1px solid #f1f5f9;">
            <a href="#" style="font-size:14px;color:#16a34a;text-decoration:none;font-weight:600;">→ &nbsp;Case study: How we helped a similar company 3× their output</a>
          </td>
        </tr>
        <tr>
          <td style="padding:8px 0;">
            <a href="#" style="font-size:14px;color:#16a34a;text-decoration:none;font-weight:600;">→ &nbsp;Free ROI calculator — estimate your time savings</a>
          </td>
        </tr>
      </table>

      <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 28px;">
        <tr>
          <td align="center">
            <a href="#" style="display:inline-block;background-color:#14532d;background:linear-gradient(135deg,#14532d,#16a34a);color:#fff;font-size:15px;font-weight:700;text-decoration:none;padding:14px 36px;border-radius:8px;">Schedule Our Next Call →</a>
          </td>
        </tr>
      </table>

      <p style="margin:0;font-size:14px;color:#6b7280;line-height:1.7;">
        Speak soon,<br><strong style="color:#1f2937;">{sender_name}</strong><br>
        <span style="font-size:13px;color:#9ca3af;">{sender_email}</span>
      </p>
    </td>
  </tr>

  <!-- FOOTER -->
  <tr>
    <td style="background:#f0fdf4;padding:16px 40px;text-align:center;border-top:1px solid #bbf7d0;">
      <p style="margin:0;font-size:12px;color:#9ca3af;">Sent to {first_name} following your meeting.</p>
      <p style="margin:4px 0 0;font-size:12px;"><a href="#" style="color:#16a34a;text-decoration:none;">Unsubscribe</a></p>
    </td>
  </tr>

</table>
</body>
</html>""",
    },

    # ── 9. Agency / Service Proposal — Dark Navy ──────────────────────────
    {
        "name": "Agency Proposal — Navy",
        "subject": "Our proposal for {org}, {first_name}",
        "html_body": """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:20px 0;background:#f8fafc;font-family:Arial,sans-serif;">
<table align="center" width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.09);">

  <!-- HEADER -->
  <tr>
    <td bgcolor="#0c1445" style="background-color:#0c1445;background:linear-gradient(135deg,#0c1445 0%,#1e3a8a 100%);padding:40px;">
      <p style="margin:0;font-size:12px;color:#93c5fd;letter-spacing:1.5px;text-transform:uppercase;font-weight:600;">Prepared exclusively for</p>
      <h1 style="margin:8px 0;font-size:26px;font-weight:800;color:#fff;">{org}</h1>
      <p style="margin:0;font-size:14px;color:#93c5fd;">Growth Partnership Proposal · 2026</p>
    </td>
  </tr>

  <!-- INTRO -->
  <tr>
    <td style="padding:36px 40px 0;">
      <p style="margin:0 0 16px;font-size:15px;line-height:1.7;color:#1f2937;">Hi <strong>{first_name}</strong>,</p>
      <p style="margin:0 0 24px;font-size:15px;line-height:1.7;color:#374151;">
        Following our conversation, I've put together a tailored proposal for <strong>{org}</strong>. Based on what you shared, here's exactly how we'd approach your growth challenges.
      </p>
      <hr style="border:none;border-top:1px solid #e2e8f0;margin:0 0 24px;">
    </td>
  </tr>

  <!-- SCOPE -->
  <tr>
    <td style="padding:0 40px 24px;">
      <h3 style="margin:0 0 16px;font-size:16px;font-weight:700;color:#0c1445;">📌 Scope of Work</h3>
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td style="padding:10px 14px;background:#f8fafc;border-radius:6px;margin-bottom:8px;border-left:3px solid #1e3a8a;">
            <p style="margin:0;font-size:14px;color:#1e3a8a;font-weight:700;">Phase 1 — Discovery &amp; Strategy</p>
            <p style="margin:4px 0 0;font-size:13px;color:#475569;">Week 1-2 · Audit, competitor analysis, and full growth roadmap</p>
          </td>
        </tr>
      </table>
      <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:8px;">
        <tr>
          <td style="padding:10px 14px;background:#f8fafc;border-radius:6px;border-left:3px solid #7c3aed;">
            <p style="margin:0;font-size:14px;color:#7c3aed;font-weight:700;">Phase 2 — Build &amp; Launch</p>
            <p style="margin:4px 0 0;font-size:13px;color:#475569;">Week 3-6 · Implementation, automation setup, campaign launch</p>
          </td>
        </tr>
      </table>
      <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:8px;">
        <tr>
          <td style="padding:10px 14px;background:#f8fafc;border-radius:6px;border-left:3px solid #059669;">
            <p style="margin:0;font-size:14px;color:#059669;font-weight:700;">Phase 3 — Scale &amp; Optimise</p>
            <p style="margin:4px 0 0;font-size:13px;color:#475569;">Week 7+ · Monthly reporting, A/B testing, continuous improvement</p>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- INVESTMENT -->
  <tr>
    <td style="padding:0 40px 24px;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td bgcolor="#0c1445" style="background-color:#0c1445;background:linear-gradient(135deg,#0c1445,#1e3a8a);border-radius:10px;padding:24px;text-align:center;">
            <p style="margin:0;font-size:12px;color:#93c5fd;text-transform:uppercase;letter-spacing:1px;">Investment</p>
            <p style="margin:8px 0;font-size:32px;font-weight:800;color:#fff;">₹49,999 <span style="font-size:16px;font-weight:400;color:#93c5fd;">/ month</span></p>
            <p style="margin:0;font-size:13px;color:#93c5fd;">No lock-in contract · Cancel anytime</p>
          </td>
        </tr>
      </table>
    </td>
  </tr>

  <!-- CTA -->
  <tr>
    <td style="padding:0 40px 32px;">
      <table width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 16px;">
        <tr>
          <td align="center">
            <a href="#" style="display:inline-block;background-color:#0c1445;background:linear-gradient(135deg,#0c1445,#1e3a8a);color:#fff;font-size:15px;font-weight:700;text-decoration:none;padding:14px 36px;border-radius:8px;">Accept Proposal →</a>
          </td>
        </tr>
      </table>
      <p style="margin:0 0 24px;font-size:13px;color:#94a3b8;text-align:center;">Or reply to this email with any questions</p>

      <p style="margin:0;font-size:14px;color:#6b7280;line-height:1.7;">
        Looking forward to working together,<br><strong style="color:#1f2937;">{sender_name}</strong><br>
        <span style="font-size:13px;color:#9ca3af;">{sender_email}</span>
      </p>
    </td>
  </tr>

  <!-- FOOTER -->
  <tr>
    <td style="background:#f8fafc;padding:16px 40px;text-align:center;border-top:1px solid #e2e8f0;">
      <p style="margin:0;font-size:12px;color:#9ca3af;">This proposal was prepared for {first_name} at {org}.</p>
      <p style="margin:4px 0 0;font-size:12px;"><a href="#" style="color:#1e3a8a;text-decoration:none;">Unsubscribe</a></p>
    </td>
  </tr>

</table>
</body>
</html>""",
    },

]
