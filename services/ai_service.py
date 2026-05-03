import json
import re
import httpx
from fastapi import HTTPException
from config import settings
from utils.helpers import decrypt_secret

GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
]
GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

async def get_gemini_api_key(db, user_id: str) -> str:
    creds = await db.user_settings.find_one({"user_id": user_id})
    if creds and creds.get("gemini_api_key"):
        try:
            return decrypt_secret(creds["gemini_api_key"], settings.ENCRYPTION_KEY)
        except Exception:
            pass
    if settings.GEMINI_API_KEY:
        return settings.GEMINI_API_KEY
    raise HTTPException(status_code=400, detail="No Gemini API key configured. Add one in Settings → AI Settings.")

def parse_json_from_response(text: str) -> dict:
    text = text.strip()
    # Strip markdown code fences
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*```\s*$', '', text, flags=re.MULTILINE)
    text = text.strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting first JSON object from the text
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise HTTPException(status_code=502, detail="AI returned an unexpected response format. Please try again.")

async def _call_gemini(api_key: str, prompt: str) -> str:
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048}
    }
    last_error = None
    async with httpx.AsyncClient(timeout=45) as client:
        for model in GEMINI_MODELS:
            url = f"{GEMINI_BASE}/{model}:generateContent?key={api_key}"
            try:
                r = await client.post(url, json=payload)
                if r.status_code == 404:
                    continue  # model not available, try next
                if r.status_code == 400:
                    detail = r.json().get("error", {}).get("message", "Invalid request")
                    raise HTTPException(status_code=400, detail=f"Gemini API error: {detail}")
                if r.status_code == 401 or r.status_code == 403:
                    raise HTTPException(status_code=400, detail="Invalid Gemini API key. Check Settings → AI Settings.")
                if r.status_code == 429:
                    raise HTTPException(status_code=429, detail="Gemini API quota exceeded. Try again later.")
                r.raise_for_status()
                data = r.json()
                # Extract text from response
                try:
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError, TypeError):
                    raise HTTPException(status_code=502, detail="Unexpected response from Gemini API.")
            except HTTPException:
                raise
            except httpx.TimeoutException:
                raise HTTPException(status_code=504, detail="Gemini API timed out. Please try again.")
            except httpx.RequestError as e:
                last_error = str(e)
                continue

    raise HTTPException(status_code=502, detail=f"Could not reach Gemini API: {last_error}")

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
    defaults = {"subject": "", "html_body": "", "plain_text": "", "preview_text": "", "word_count": 0, "estimated_read_seconds": 0}
    return {**defaults, **data}

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
    defaults = {"subject": "", "html_body": "", "plain_text": "", "preview_text": "", "word_count": 0, "estimated_read_seconds": 0}
    return {**defaults, **data}
