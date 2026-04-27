import asyncio
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import settings
from backend.utils.helpers import get_current_timestamp

async def seed_data():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]
    
    # Example User ID (should be replaced with actual user id or run for all users)
    # This is a template for the admin to use as a base
    
    templates = [
        {
            "name": "Modern B2B Outreach",
            "subject": "Quick question regarding {company}",
            "html_body": """
            <div style="max-width: 600px; margin: 0 auto; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #1f2937; padding: 40px; border: 1px solid #e5e7eb; border-radius: 8px; background-color: #ffffff;">
                <p style="font-size: 16px; margin-bottom: 24px;">Hi {first_name},</p>
                
                <p style="font-size: 16px; margin-bottom: 24px;">I was recently looking into <strong>{company}</strong> and was impressed by your recent growth in the industry. It seems like you're doing some incredible work.</p>
                
                <p style="font-size: 16px; margin-bottom: 24px;">I'm reaching out because we've helped similar organizations streamline their outreach operations and I thought there might be a fit here as well.</p>
                
                <div style="margin: 32px 0; text-align: center;">
                    <a href="https://example.com/demo" style="background-color: #2563eb; color: #ffffff; padding: 12px 24px; border-radius: 6px; text-decoration: none; font-weight: 600; display: inline-block;">Schedule a 10-Min Chat</a>
                </div>
                
                <p style="font-size: 16px; margin-bottom: 24px;">Do you have any time later this week for a brief conversation?</p>
                
                <div style="border-top: 1px solid #e5e7eb; padding-top: 24px; margin-top: 32px; font-size: 14px; color: #6b7280;">
                    Best regards,<br>
                    <strong>Stark</strong><br>
                    CEO at BulkReach Pro
                </div>
            </div>
            """
        },
        {
            "name": "Soft Value-Add",
            "subject": "Thought you might find this interesting, {first_name}",
            "html_body": """
            <div style="max-width: 600px; margin: 0 auto; font-family: -apple-system, sans-serif; line-height: 1.5; color: #333; padding: 20px; border-radius: 12px; border: 1px solid #eee;">
                <h2 style="color: #2563eb; font-size: 20px; margin-top: 0;">Hey {first_name},</h2>
                
                <p>I came across an article today about the future of B2B automation and immediately thought of <strong>{company}</strong>.</p>
                
                <p>Given your role, I figured you'd find the insights on personalized outreach particularly relevant.</p>
                
                <blockquote style="border-left: 4px solid #2563eb; padding-left: 16px; margin: 24px 0; font-style: italic; color: #555;">
                    "The most successful companies in 2024 aren't just sending more emails—they're sending better ones."
                </blockquote>
                
                <p>Would you be open to a quick exchange of ideas on how you're currently handling this at {company}?</p>
                
                <p style="margin-top: 30px;">
                    Cheers,<br>
                    <strong>The BulkReach Team</strong>
                </p>
            </div>
            """
        }
    ]
    
    # For now, we'll just print them or insert for a specific user if provided
    print("Seeding 'Attractive' templates...")
    # await db.mail_templates.insert_many(...)
    print("Done. Use these as reference for 'Attractive' emails.")

if __name__ == "__main__":
    asyncio.run(seed_data())
