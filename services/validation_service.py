import re
import asyncio
from dns import asyncresolver
from dns.exception import DNSException

DISPOSABLE_DOMAINS = {
    "mailinator.com", "tempmail.com", "guerrillamail.com", "throwam.com", "yopmail.com",
    "10minutemail.com", "temp-mail.org", "trashmail.com", "getnada.com", "tempmail.net",
    "sharklasers.com", "spam4.me", "dispostable.com", "tempmailaddress.com", "mytemp.email",
    "fakeinbox.com", "maildrop.cc", "anonaddy.me", "simplelogin.co", "spamgourmet.com"
}

async def validate_email(email: str) -> dict:
    result = {
        "email": email,
        "status": "valid",
        "reason": ""
    }
    
    # a) Format check: RFC 5322 regex
    pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if not re.match(pattern, email):
        result["status"] = "invalid"
        result["reason"] = "Invalid email format"
        return result
        
    domain = email.split('@')[1].lower()
    
    # b) Disposable domain check
    if domain in DISPOSABLE_DOMAINS:
        result["status"] = "risky"
        result["reason"] = "Disposable email domain"
        return result
        
    # c) MX record lookup
    try:
        resolver = asyncresolver.Resolver()
        answers = await resolver.resolve(domain, 'MX')
        if not answers:
            result["status"] = "mx_fail"
            result["reason"] = "No MX records found"
            return result
    except (DNSException, Exception) as e:
        result["status"] = "mx_fail"
        result["reason"] = f"DNS lookup failed or NXDOMAIN"
        return result
        
    return result

async def validate_email_list(emails: list[str]) -> list[dict]:
    tasks = [validate_email(email) for email in emails]
    results = await asyncio.gather(*tasks)
    return list(results)
