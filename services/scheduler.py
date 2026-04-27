from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from core.database import get_db
from services.email_sender import send_email
from services.ai_generator import generate_personalized_content
from datetime import datetime
import asyncio

scheduler = AsyncIOScheduler()

async def process_campaigns():
    db = get_db()
    
    running_campaigns = await db.campaigns.find({"status": "running"}).to_list(None)
    for campaign in running_campaigns:
        pending_recipients = await db.recipients.find({
            "campaign_id": campaign["_id"],
            "status": "pending"
        }).limit(50).to_list(None)
        
        if not pending_recipients:
            # Check if all sent
            total_pending = await db.recipients.count_documents({
                "campaign_id": campaign["_id"],
                "status": "pending"
            })
            if total_pending == 0:
                await db.campaigns.update_one(
                    {"_id": campaign["_id"]},
                    {"$set": {"status": "completed", "updated_at": datetime.utcnow()}}
                )
            continue
            
        for recipient in pending_recipients:
            try:
                subject = campaign["subject_template"]
                body = campaign["body_template"]
                
                # Simple placeholder replacement
                for key, value in recipient.get("metadata", {}).items():
                    subject = subject.replace(f"{{{{{key}}}}}", str(value))
                    body = body.replace(f"{{{{{key}}}}}", str(value))
                if recipient.get("name"):
                    subject = subject.replace("{{name}}", recipient["name"])
                    body = body.replace("{{name}}", recipient["name"])
                
                if campaign.get("use_ai_personalization"):
                    body = await generate_personalized_content(
                        user_id=campaign["user_id"],
                        template=body,
                        recipient_data=recipient.get("metadata", {})
                    )
                
                success = await send_email(
                    user_id=campaign["user_id"],
                    to_email=recipient["email"],
                    subject=subject,
                    body=body
                )
                
                if success:
                    await db.recipients.update_one(
                        {"_id": recipient["_id"]},
                        {"$set": {"status": "sent", "sent_at": datetime.utcnow()}}
                    )
                    await db.campaigns.update_one(
                        {"_id": campaign["_id"]},
                        {"$inc": {"sent_count": 1}}
                    )
                else:
                    await db.recipients.update_one(
                        {"_id": recipient["_id"]},
                        {"$set": {"status": "failed", "error_message": "SMTP failed"}}
                    )
            except Exception as e:
                await db.recipients.update_one(
                    {"_id": recipient["_id"]},
                    {"$set": {"status": "failed", "error_message": str(e)}}
                )
            await asyncio.sleep(1) # Simple rate limiting

def start_scheduler():
    scheduler.add_job(process_campaigns, IntervalTrigger(minutes=1))
    scheduler.start()
