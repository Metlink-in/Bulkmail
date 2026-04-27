import json
import asyncio
import google.generativeai as genai
from fastapi import HTTPException
from backend.config import settings
from backend.utils.helpers import decrypt_secret

async def get_gemini_api_key(db, user_id: str) -> str:
    creds = await db.user_credentials.find_one({"user_id": user_id})
    if creds and creds.get("gemini_api_key"):
        return decrypt_secret(creds["gemini_api_key"], settings.ENCRYPTION_KEY)
    if settings.GEMINI_API_KEY:
        return settings.GEMINI_API_KEY
    raise HTTPException(status_code=400, detail="No Gemini API key configured")

def parse_json_from_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    try:
        data = json.loads(text.strip())
        return data
    except json.JSONDecodeError:
        raise ValueError("Failed to parse valid JSON from AI response")

async def compose_email(
    db, user_id: str,
    goal: str, industry: str, tone: str,
    sender_name: str, sender_company: str,
    value_prop: str, recipient_name: str = "there"
) -> dict:
    api_key = await get_gemini_api_key(db, user_id)
    genai.configure(api_key=api_key)
    # Using the requested model parameter, wrapped in a generic flash implementation
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
    except Exception:
        model = genai.GenerativeModel("gemini-1.5-flash")
    
    PROMPT = f"""
    You are an expert B2B cold email copywriter.
    Write a cold outreach email with:
    - Goal: {goal}
    - Target industry: {industry}
    - Tone: {tone}
    - From: {sender_name} at {sender_company}
    - Value proposition: {value_prop}

    Requirements:
    - Subject: under 60 chars, curiosity-driven, high open rate
    - Body: 3-4 short paragraphs, under 200 words total
    - Opening: personalized with {{first_name}} placeholder
    - One clear CTA in last paragraph
    - Professional signature with {sender_name} and {sender_company}
    - NO spam words: free, winner, urgent, guaranteed, limited time, act now

    DESIGN REQUIREMENTS for html_body:
    - Use a clean, modern B2B look.
    - Container: Max-width 600px, centered, padding 40px.
    - Typography: Use system fonts (sans-serif), line-height 1.6, font-size 16px.
    - Subtle borders or soft shadows for a "card" feel if appropriate.
    - Use a professional accent color for links and CTA buttons (e.g., a nice blue #2563eb).
    - Signature should be subtly styled with slightly smaller, muted text.
    - Ensure it looks GREAT on both mobile and desktop.

    Return ONLY valid JSON (no markdown, no backticks, just raw JSON):
    {{
      "subject": "...",
      "html_body": "...",
      "plain_text": "...",
      "preview_text": "...",
      "word_count": 0,
      "estimated_read_seconds": 0
    }}
    html_body must be complete HTML with inline CSS styles for email clients.
    """
    
    response = await asyncio.to_thread(model.generate_content, PROMPT)
    data = parse_json_from_response(response.text)
    
    required_keys = ["subject", "html_body", "plain_text", "preview_text", "word_count", "estimated_read_seconds"]
    for k in required_keys:
        if k not in data:
            data[k] = ""
            
    return data

async def improve_email(
    db, user_id: str,
    current_subject: str, current_html_body: str, instruction: str
) -> dict:
    api_key = await get_gemini_api_key(db, user_id)
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
    except Exception:
        model = genai.GenerativeModel("gemini-1.5-flash")
    
    PROMPT = f"""
    You are an expert B2B cold email copywriter.
    Improve the following email based on this instruction: {instruction}
    
    Current Subject: {current_subject}
    Current Body: {current_html_body}
    
    Requirements:
    - Subject: under 60 chars
    - Body: under 200 words total
    - Opening: keep personalization placeholders like {{first_name}}
    - Maintain or enhance the "Attractive & Professional" B2B styling.
    - Standardize font-size to 16px and line-height to 1.6 for readability.
    
    Return ONLY valid JSON:
    {{
      "subject": "...",
      "html_body": "...",
      "plain_text": "...",
      "preview_text": "...",
      "word_count": 0,
      "estimated_read_seconds": 0
    }}
    html_body must be complete HTML with inline CSS styles for email clients.
    """
    
    response = await asyncio.to_thread(model.generate_content, PROMPT)
    data = parse_json_from_response(response.text)
    
    required_keys = ["subject", "html_body", "plain_text", "preview_text", "word_count", "estimated_read_seconds"]
    for k in required_keys:
        if k not in data:
            data[k] = ""
            
    return data
