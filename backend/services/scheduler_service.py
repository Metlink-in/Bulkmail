from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from backend.database import get_db
from datetime import datetime
import asyncio

scheduler = AsyncIOScheduler()

async def check_and_queue_pending_jobs(db):
    from backend.utils.helpers import get_current_timestamp
    now = get_current_timestamp()
    
    cursor = db.mail_jobs.find({
        "status": "queued",
        "scheduled_at": {"$lte": now}
    })
    
    async for job in cursor:
        job_id = str(job["_id"])
        
        # ensure it's not already running in scheduler
        if not scheduler.get_job(f"job_{job_id}"):
            scheduler.add_job(
                process_mail_job_wrapper,
                DateTrigger(run_date=now),
                args=[job_id],
                id=f"job_{job_id}",
                replace_existing=True
            )

async def start_scheduler(db):
    if not scheduler.running:
        scheduler.start()
        scheduler.add_job(
            check_and_queue_pending_jobs, 
            IntervalTrigger(minutes=1),
            args=[db],
            id="check_pending_jobs",
            replace_existing=True
        )

async def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()

async def process_mail_job_wrapper(job_id: str):
    from backend.services.mail_service import process_mail_job
    db = await get_db()
    await process_mail_job(db, job_id)

async def schedule_job(db, job_id: str, run_at: datetime):
    scheduler.add_job(
        process_mail_job_wrapper,
        DateTrigger(run_date=run_at),
        args=[job_id],
        id=f"job_{job_id}",
        replace_existing=True
    )

async def schedule_recurring(db, task_id: str, cron_expression: str):
    scheduler.add_job(
        create_and_run_recurring_job,
        CronTrigger.from_crontab(cron_expression),
        args=[db, task_id],
        id=f"task_{task_id}",
        replace_existing=True
    )

async def create_and_run_recurring_job(db, task_id: str):
    # Fetch scheduled_task, create mail_job, run
    from backend.utils.helpers import get_current_timestamp
    import uuid
    task = await db.scheduled_tasks.find_one({"_id": task_id})
    if not task or not task.get("is_active"):
        return
        
    job_id = str(uuid.uuid4())
    job = {
        "_id": job_id,
        "user_id": task["user_id"],
        "template_id": task["template_id"],
        "contact_ids": task.get("contact_ids", []),
        "status": "queued",
        "created_at": get_current_timestamp(),
        "updated_at": get_current_timestamp(),
        "scheduled_at": get_current_timestamp()
    }
    await db.mail_jobs.insert_one(job)
    await process_mail_job_wrapper(job_id)

async def cancel_scheduled_job(job_id: str):
    try:
        scheduler.remove_job(f"job_{job_id}")
    except:
        pass
    try:
        scheduler.remove_job(f"task_{job_id}")
    except:
        pass

async def get_all_scheduled_jobs() -> list:
    jobs = scheduler.get_jobs()
    return [{"id": j.id, "next_run_time": j.next_run_time} for j in jobs]
