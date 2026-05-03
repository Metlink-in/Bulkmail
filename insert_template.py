"""Run once: python insert_template.py"""
import asyncio, uuid
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from utils.helpers import get_current_timestamp

METLINK_HTML = """<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Metlink Outreach</title>
</head>

<body style="margin:0; padding:0; background-color:#f4f7fb; font-family:Arial, sans-serif;">

  <table align="center" width="600" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:10px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,0.08);">

    <!-- Header -->
    <tr>
      <td style="background:linear-gradient(90deg, #4A00E0, #8E2DE2); padding:25px; text-align:center; color:white;">
        <h1 style="margin:0; font-size:26px;">Metlink</h1>
        <p style="margin:5px 0 0; font-size:14px;">Smart Solutions. Real Growth.</p>
      </td>
    </tr>

    <!-- Body -->
    <tr>
      <td style="padding:30px; color:#333;">

        <h2 style="margin-top:0; color:#4A00E0;">Let's Help You Scale Faster 🚀</h2>

        <p style="font-size:15px; line-height:1.6;">
          Hi <strong>{first_name}</strong>,
        </p>

        <p style="font-size:15px; line-height:1.6;">
          I came across your work at <strong>{org}</strong> and noticed how you're building in the <strong>{{industry}}</strong> space.
        </p>

        <p style="font-size:15px; line-height:1.6;">
          At <strong>Metlink</strong>, we help businesses like yours streamline operations, automate workflows, and unlock scalable growth using modern tech and AI-driven systems.
        </p>

        <!-- Highlight Box -->
        <div style="background:#f1efff; padding:15px; border-radius:8px; margin:20px 0;">
          <p style="margin:0; font-size:14px;">
            ⚡ <strong>What we can help with:</strong><br>
            • Automation &amp; AI integration<br>
            • Custom web &amp; backend systems<br>
            • Growth-focused digital solutions
          </p>
        </div>

        <p style="font-size:15px; line-height:1.6;">
          Would you be open to a quick 15-minute chat to explore if this aligns with your current goals?
        </p>

        <!-- CTA Button -->
        <div style="text-align:center; margin:30px 0;">
          <a href="{{cta_link}}" style="background:#4A00E0; color:#fff; text-decoration:none; padding:12px 25px; border-radius:6px; font-size:15px; display:inline-block;">
            Book a Quick Call
          </a>
        </div>

        <p style="font-size:14px; color:#777;">
          Looking forward to connecting.<br><br>
          <strong>{{your_name}}</strong><br>
          Metlink Team
        </p>

      </td>
    </tr>

    <!-- Footer -->
    <tr>
      <td style="background:#f4f7fb; padding:15px; text-align:center; font-size:12px; color:#888;">
        © 2026 Metlink | All rights reserved<br>
        <a href="{{unsubscribe_link}}" style="color:#8E2DE2; text-decoration:none;">Unsubscribe</a>
      </td>
    </tr>

  </table>

</body>
</html>"""

async def main():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DB_NAME]

    existing = await db.mail_templates.find_one({"name": "Metlink Outreach", "is_global": True})
    if existing:
        print("✅ Metlink Outreach template already exists — updating HTML...")
        await db.mail_templates.update_one(
            {"_id": existing["_id"]},
            {"$set": {"html_body": METLINK_HTML.strip(), "updated_at": get_current_timestamp()}}
        )
        print("✅ Updated.")
    else:
        now = get_current_timestamp()
        doc = {
            "_id": str(uuid.uuid4()),
            "is_global": True,
            "user_id": "global",
            "name": "Metlink Outreach",
            "subject": "Quick question for {first_name} at {org}",
            "html_body": METLINK_HTML.strip(),
            "created_at": now,
            "updated_at": now,
        }
        await db.mail_templates.insert_one(doc)
        print("✅ Inserted Metlink Outreach global template.")

    client.close()

if __name__ == "__main__":
    asyncio.run(main())
