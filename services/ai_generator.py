import google.generativeai as genai
from core.database import get_db
from core.crypto import decrypt_value
from typing import Dict, Any

async def generate_personalized_content(user_id: str, template: str, recipient_data: Dict[str, Any]) -> str:
    db = get_db()
    user = await db.users.find_one({"_id": user_id})
    if not user or not user.get("ai_config"):
        raise ValueError("AI configuration not found for user")
        
    api_key = decrypt_value(user["ai_config"]["gemini_api_key"])
    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"Personalize the following email template for a recipient. " \
             f"Template: {template}\n" \
             f"Recipient Data: {recipient_data}\n" \
             f"Return ONLY the personalized text without any extra chat."
             
    response = model.generate_content(prompt)
    return response.text.strip()
