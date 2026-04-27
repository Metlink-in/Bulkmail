from fastapi import APIRouter, Depends, HTTPException
from core.database import get_db
from core.security import get_current_user
from models.campaign import CampaignCreate, CampaignResponse
import uuid
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])

@router.post("/", response_model=CampaignResponse)
async def create_campaign(campaign: CampaignCreate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    campaign_id = str(uuid.uuid4())
    
    new_campaign = {
        "_id": campaign_id,
        "user_id": current_user["user_id"],
        "name": campaign.name,
        "subject_template": campaign.subject_template,
        "body_template": campaign.body_template,
        "use_ai_personalization": campaign.use_ai_personalization,
        "status": "draft",
        "sent_count": 0,
        "total_recipients": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.campaigns.insert_one(new_campaign)
    return CampaignResponse(**new_campaign, id=campaign_id)

@router.get("/", response_model=List[CampaignResponse])
async def list_campaigns(current_user: dict = Depends(get_current_user)):
    db = get_db()
    cursor = db.campaigns.find({"user_id": current_user["user_id"]}).sort("created_at", -1)
    campaigns = await cursor.to_list(length=100)
    
    result = []
    for c in campaigns:
        c["id"] = c["_id"]
        result.append(CampaignResponse(**c))
    return result

@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    campaign = await db.campaigns.find_one({"_id": campaign_id, "user_id": current_user["user_id"]})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    campaign["id"] = campaign["_id"]
    return CampaignResponse(**campaign)

@router.post("/{campaign_id}/start")
async def start_campaign(campaign_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    campaign = await db.campaigns.find_one({"_id": campaign_id, "user_id": current_user["user_id"]})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    # Check if user has SMTP configured
    user = await db.users.find_one({"_id": current_user["user_id"]})
    if not user.get("smtp_config"):
        raise HTTPException(status_code=400, detail="SMTP configuration missing")
        
    if campaign.get("use_ai_personalization") and not user.get("ai_config"):
        raise HTTPException(status_code=400, detail="AI configuration missing")
        
    await db.campaigns.update_one(
        {"_id": campaign_id},
        {"$set": {"status": "running", "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Campaign started"}

@router.post("/{campaign_id}/pause")
async def pause_campaign(campaign_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    result = await db.campaigns.update_one(
        {"_id": campaign_id, "user_id": current_user["user_id"], "status": "running"},
        {"$set": {"status": "paused", "updated_at": datetime.utcnow()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Campaign not found or not running")
        
    return {"message": "Campaign paused"}
