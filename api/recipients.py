from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from core.database import get_db
from core.security import get_current_user
from models.recipient import RecipientCreate, RecipientResponse
import uuid
import csv
from io import StringIO
from typing import List

router = APIRouter(prefix="/api/recipients", tags=["recipients"])

@router.post("/", response_model=RecipientResponse)
async def add_recipient(recipient: RecipientCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    campaign = await db.campaigns.find_one({"_id": recipient.campaign_id, "user_id": current_user["user_id"]})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    recipient_id = str(uuid.uuid4())
    new_recipient = {
        "_id": recipient_id,
        "campaign_id": recipient.campaign_id,
        "user_id": current_user["user_id"],
        "email": recipient.email,
        "name": recipient.name,
        "metadata": recipient.metadata,
        "status": "pending",
        "sent_at": None,
        "error_message": None
    }
    
    await db.recipients.insert_one(new_recipient)
    await db.campaigns.update_one(
        {"_id": recipient.campaign_id},
        {"$inc": {"total_recipients": 1}}
    )
    
    new_recipient["id"] = recipient_id
    return RecipientResponse(**new_recipient)

@router.post("/bulk/{campaign_id}")
async def upload_csv(campaign_id: str, file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    db = get_db()
    campaign = await db.campaigns.find_one({"_id": campaign_id, "user_id": current_user["user_id"]})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
        
    contents = await file.read()
    decoded = contents.decode("utf-8")
    reader = csv.DictReader(StringIO(decoded))
    
    recipients_to_insert = []
    for row in reader:
        if 'email' not in row:
            continue
            
        metadata = {k: v for k, v in row.items() if k not in ['email', 'name']}
        recipients_to_insert.append({
            "_id": str(uuid.uuid4()),
            "campaign_id": campaign_id,
            "user_id": current_user["user_id"],
            "email": row['email'],
            "name": row.get('name'),
            "metadata": metadata,
            "status": "pending",
            "sent_at": None,
            "error_message": None
        })
        
    if recipients_to_insert:
        await db.recipients.insert_many(recipients_to_insert)
        await db.campaigns.update_one(
            {"_id": campaign_id},
            {"$inc": {"total_recipients": len(recipients_to_insert)}}
        )
        
    return {"message": f"Successfully imported {len(recipients_to_insert)} recipients"}

@router.get("/{campaign_id}", response_model=List[RecipientResponse])
async def list_recipients(campaign_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    campaign = await db.campaigns.find_one({"_id": campaign_id, "user_id": current_user["user_id"]})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    cursor = db.recipients.find({"campaign_id": campaign_id, "user_id": current_user["user_id"]})
    recipients = await cursor.to_list(length=1000)
    
    result = []
    for r in recipients:
        r["id"] = r["_id"]
        result.append(RecipientResponse(**r))
    return result
