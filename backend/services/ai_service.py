import json
import httpx
from fastapi import HTTPException
from backend.config import settings
from backend.utils.helpers import decrypt_secret

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

async def get_gemini_api_key(db, user_id: str) -> str:
    creds = await db.user_settings.find_one({"user_id": user_id})
    if creds and creds.get("gemini_api_key"):
        return decrypt_secret(creds["gemini_api_key"], settings.ENCRYPTION_KEY)
    if settings.GEMINI_API_KEY:
        return settings.GEMINI_API_KEY
    raise HTTPException(status_code=400, detail="No Gemini API key configured. Add one in Settings.")

def parse_json_from_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        raise ValueError("Failed to parse valid JSON from AI response")

async def _call_gemini(api_key: str, prompt: str) -> str:
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048}
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{GEMINI_URL}?key={api_key}", json=payload)
        r.raise_for_status()
        data = r.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

async def compose_email(
    db, user_id: str,
    goal: str, industry: str, tone: str,
    sender_name: str, sender_company: str,
    value_prop: str, recipient_name: str = "there"
) -> dict:
    api_key = await get_gemini_api_key(db, user_id)

    prompt = f"""You are an expert B2B cold email copywriter.
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

DESIGN for html_body:
- Clean modern B2B look, max-width 600px, centered, padding 40px
- System fonts (sans-serif), line-height 1.6, font-size 16px
- Professional accent color for links/buttons (#2563eb)
- Signature with smaller muted text
- Mobile-friendly

Return ONLY valid JSON (no markdown, no backticks):
{{
  "subject": "...",
  "html_body": "...",
  "plain_text": "...",
  "preview_text": "...",
  "word_count": 0,
  "estimated_read_seconds": 0
}}
html_body must be complete HTML with inline CSS."""

    text = await _call_gemini(api_key, prompt)
    data = parse_json_from_response(text)
    for k in ["subject", "html_body", "plain_text", "preview_text", "word_count", "estimated_read_seconds"]:
        if k not in data:
            data[k] = ""
    return data

async def improve_email(
    db, user_id: str,
    current_subject: str, current_html_body: str, instruction: str
) -> dict:
    api_key = await get_gemini_api_key(db, user_id)

    prompt = f"""You are an expert B2B cold email copywriter.
Improve the following email based on this instruction: {instruction}

Current Subject: {current_subject}
Current Body: {current_html_body}

Requirements:
- Subject: under 60 chars
- Body: under 200 words total
- Keep personalization placeholders like {{first_name}}
- Maintain professional B2B styling, font-size 16px, line-height 1.6

Return ONLY valid JSON:
{{
  "subject": "...",
  "html_body": "...",
  "plain_text": "...",
  "preview_text": "...",
  "word_count": 0,
  "estimated_read_seconds": 0
}}
html_body must be complete HTML with inline CSS."""

    text = await _call_gemini(api_key, prompt)
    data = parse_json_from_response(text)
    for k in ["subject", "html_body", "plain_text", "preview_text", "word_count", "estimated_read_seconds"]:
        if k not in data:
            data[k] = ""
    return data
