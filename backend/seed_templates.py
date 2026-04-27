import os
import asyncio
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

async def seed_templates():
    load_dotenv()
    uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME", "bulkreach_prod")
    client = AsyncIOMotorClient(uri)
    db = client[db_name]

    templates = [
        {
            "_id": "tpl_premium_outreach",
            "user_id": "SYSTEM",
            "is_global": True,
            "name": "Premium Outreach (Modern)",
            "subject": "Quick question regarding {company}",
            "html_body": """
            <div style="background-color: #f6f9fc; padding: 40px 0; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                    <div style="background-color: #ff6b35; padding: 20px; text-align: center;">
                        <h1 style="color: #ffffff; margin: 0; font-size: 24px; letter-spacing: 1px;">OUTREACH</h1>
                    </div>
                    <div style="padding: 40px;">
                        <p style="font-size: 16px; color: #32325d; line-height: 24px;">Hi {first_name},</p>
                        <p style="font-size: 16px; color: #525f7f; line-height: 26px;">
                            I've been following <strong>{company}</strong> for a while and I'm really impressed with your recent growth. 
                            I'm reaching out because I believe our tool can help you scale your operations even faster.
                        </p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="#" style="background-color: #ff6b35; color: #ffffff; padding: 12px 30px; border-radius: 5px; text-decoration: none; font-weight: 600; display: inline-block;">Schedule a Demo</a>
                        </div>
                        <p style="font-size: 16px; color: #525f7f; line-height: 26px;">
                            Would you be open to a 10-minute chat next Tuesday?
                        </p>
                        <p style="font-size: 16px; color: #32325d; margin-top: 40px; border-top: 1px solid #e6ebf1; padding-top: 20px;">
                            Best regards,<br>
                            <strong>Stark Industries</strong>
                        </p>
                    </div>
                </div>
            </div>
            """,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "_id": "tpl_product_announcement",
            "user_id": "SYSTEM",
            "is_global": True,
            "name": "Product Announcement (Sleek)",
            "subject": "Introducing the new BulkReach Engine 🚀",
            "html_body": """
            <div style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #0f172a; color: #f8fafc;">
                <table width="100%" border="0" cellpadding="0" cellspacing="0" style="padding: 40px 20px;">
                    <tr>
                        <td align="center">
                            <table width="600" border="0" cellpadding="0" cellspacing="0" style="background-color: #1e293b; border-radius: 16px; overflow: hidden; border: 1px solid #334155;">
                                <tr>
                                    <td style="padding: 60px 40px; text-align: center;">
                                        <div style="display: inline-block; background: linear-gradient(135deg, #ff6b35 0%, #ff9e7d 100%); padding: 12px; border-radius: 12px; margin-bottom: 24px;">
                                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path></svg>
                                        </div>
                                        <h1 style="font-size: 32px; font-weight: 800; margin-bottom: 16px; color: #ffffff;">The Future of Outreach.</h1>
                                        <p style="font-size: 18px; line-height: 1.6; color: #94a3b8; margin-bottom: 32px;">
                                            Hey {first_name}, we've completely rebuilt our engine to give you better deliverability.
                                        </p>
                                        <a href="#" style="background-color: #ff6b35; color: #ffffff; padding: 16px 40px; border-radius: 8px; text-decoration: none; font-weight: 700; font-size: 16px; display: inline-block;">Explore Now</a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </div>
            """,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "_id": "tpl_follow_up",
            "user_id": "SYSTEM",
            "is_global": True,
            "name": "Gentle Follow-up",
            "subject": "Thoughts on our last conversation?",
            "html_body": """
            <div style="font-family: sans-serif; max-width: 600px; line-height: 1.6; color: #333;">
                <p>Hi {first_name},</p>
                <p>I wanted to quickly follow up on my last email. I know you're busy managing things at <strong>{company}</strong>, so I didn't want this to get buried.</p>
                <p>Do you have 5 minutes this week for a brief sync?</p>
                <p>Best,<br>Jitesh</p>
            </div>
            """,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "_id": "tpl_webinar_invite",
            "user_id": "SYSTEM",
            "is_global": True,
            "name": "Webinar Invitation",
            "subject": "Invitation: Scaling {company} in 2024",
            "html_body": """
            <div style="background-color: #f4f4f5; padding: 30px;">
                <div style="background-color: white; padding: 40px; border-radius: 12px; border: 1px solid #e4e4e7;">
                    <span style="background-color: #ff6b35; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;">LIVE EVENT</span>
                    <h1 style="margin-top: 16px;">How to boost {company}'s revenue</h1>
                    <p style="color: #71717a;">Join us for an exclusive session with industry experts.</p>
                    <hr style="border: 0; border-top: 1px solid #f4f4f5; margin: 24px 0;">
                    <div style="display: flex; gap: 20px;">
                        <div><strong>DATE:</strong><br>Next Thursday</div>
                        <div><strong>TIME:</strong><br>10:00 AM EST</div>
                    </div>
                    <a href="#" style="display: inline-block; background-color: #000; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; margin-top: 24px; font-weight: bold;">Save My Spot</a>
                </div>
            </div>
            """,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "_id": "tpl_partnership",
            "user_id": "SYSTEM",
            "is_global": True,
            "name": "Partnership Proposal",
            "subject": "Partnership opportunity for {company}",
            "html_body": """
            <div style="font-family: 'Inter', sans-serif; padding: 20px;">
                <h2>Let's build something together.</h2>
                <p>Hi {first_name},</p>
                <p>I've been looking at what <strong>{company}</strong> is doing in the market and I see a lot of synergy with our current initiatives.</p>
                <p>I'd love to discuss how we can partner up to provide more value to our joint customers.</p>
                <p>Are you the right person to talk to about this?</p>
            </div>
            """,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "_id": "tpl_feedback",
            "user_id": "SYSTEM",
            "is_global": True,
            "name": "Customer Feedback",
            "subject": "How are we doing, {first_name}?",
            "html_body": """
            <div style="text-align: center; padding: 40px; font-family: sans-serif;">
                <h2 style="color: #333;">Your opinion matters.</h2>
                <p style="color: #666;">Hi {first_name}, thanks for being a part of BulkReach Pro. We'd love to hear your thoughts on how we can improve.</p>
                <div style="margin: 30px 0;">
                    <span style="font-size: 30px; margin: 0 10px; cursor: pointer;">😞</span>
                    <span style="font-size: 30px; margin: 0 10px; cursor: pointer;">😐</span>
                    <span style="font-size: 30px; margin: 0 10px; cursor: pointer;">😊</span>
                </div>
                <p style="font-size: 12px; color: #999;">It takes less than 30 seconds.</p>
            </div>
            """,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "_id": "tpl_reengagement",
            "user_id": "SYSTEM",
            "is_global": True,
            "name": "Re-engagement",
            "subject": "We miss you at {company}",
            "html_body": """
            <div style="background: linear-gradient(to bottom, #ffffff, #f9fafb); padding: 50px 20px; text-align: center; font-family: sans-serif;">
                <h1 style="color: #111827;">It's been a while...</h1>
                <p style="color: #4b5563; max-width: 400px; margin: 20px auto;">We noticed you haven't used BulkReach lately. We've added a lot of new features that we think you'll love.</p>
                <a href="#" style="display: inline-block; border: 2px solid #000; color: #000; padding: 10px 30px; text-decoration: none; font-weight: bold; margin-top: 20px;">See What's New</a>
            </div>
            """,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "_id": "tpl_meeting_request",
            "user_id": "SYSTEM",
            "is_global": True,
            "name": "Direct Meeting Request",
            "subject": "Meeting request: {first_name} <> Jitesh",
            "html_body": """
            <div style="font-family: monospace; color: #000; padding: 20px; border: 1px solid #000;">
                <p>> START COMMUNICATION</p>
                <p>TO: {first_name} @ {company}</p>
                <p>BODY: I want to show you how to automate your entire outreach workflow.</p>
                <p>REQ: 15 minutes of your time.</p>
                <p>LINK: <a href="#">[CALENDAR_URL]</a></p>
                <p>> END</p>
            </div>
            """,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "_id": "tpl_post_call",
            "user_id": "SYSTEM",
            "is_global": True,
            "name": "Post-Call Thank You",
            "subject": "Great speaking with you, {first_name}",
            "html_body": """
            <div style="font-family: sans-serif; color: #374151; padding: 20px;">
                <p>Hi {first_name},</p>
                <p>Thank you for taking the time to chat today about <strong>{company}</strong>. I really enjoyed our conversation and hearing about your goals for this quarter.</p>
                <p>As promised, here is the additional info we discussed: <a href="#">[LINK]</a></p>
                <p>Looking forward to our next steps.</p>
            </div>
            """,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        },
        {
            "_id": "tpl_cold_sales",
            "user_id": "SYSTEM",
            "is_global": True,
            "name": "Cold Sales Pitch",
            "subject": "Increase {company} leads by 40%",
            "html_body": """
            <div style="background-color: #000; color: #fff; padding: 60px 40px; font-family: sans-serif;">
                <h1 style="font-size: 40px; margin-bottom: 20px;">Ready to grow?</h1>
                <p style="font-size: 18px; color: #ccc; margin-bottom: 40px;">Stop wasting time on manual outreach. Let our AI do the heavy lifting for <strong>{company}</strong>.</p>
                <a href="#" style="background-color: #ff6b35; color: #fff; padding: 20px 40px; text-decoration: none; font-weight: bold; font-size: 18px;">Start Free Trial</a>
            </div>
            """,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
    ]

    for t in templates:
        await db.mail_templates.update_one(
            {"_id": t["_id"]},
            {"$set": t},
            upsert=True
        )
    
    print(f"✓ Seeded {len(templates)} global templates.")

if __name__ == "__main__":
    asyncio.run(seed_templates())
