import io
import csv
from datetime import datetime, timezone
import uuid
from services.validation_service import validate_email

def _clean(val):
    v = str(val).strip() if val is not None else ""
    return None if v.lower() in ("nan", "", "none") else v

async def parse_csv(file_bytes: bytes) -> list[dict]:
    text = file_bytes.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    contacts = []
    for row in reader:
        row = {k.lower().strip(): v for k, v in row.items()}
        email = _clean(row.get("email", ""))
        if not email or "@" not in email:
            continue
        name = _clean(row.get("name", ""))
        org  = _clean(row.get("org", ""))
        custom_fields = {
            k: v for k, v in row.items()
            if k not in ("email", "name", "org") and _clean(v)
        }
        validation = await validate_email(email)
        contacts.append({
            "email": email,
            "name": name,
            "org": org,
            "custom_fields": custom_fields,
            "email_status": validation["status"]
        })
    return contacts

async def import_from_sheets(sheet_url: str, api_key: str, range_name: str) -> list[dict]:
    try:
        import gspread
        gc = gspread.api_key(api_key)
        sheet_id = sheet_url.split('/d/')[1].split('/')[0]
        spreadsheet = gc.open_by_key(sheet_id)
        worksheet = spreadsheet.sheet1
        if range_name:
            records = worksheet.get(range_name)
            if not records:
                return []
            headers = [str(h).lower().strip() for h in records[0]]
            rows = [dict(zip(headers, r)) for r in records[1:]]
        else:
            rows = worksheet.get_all_records()
            rows = [{k.lower().strip(): v for k, v in r.items()} for r in rows]

        contacts = []
        for row in rows:
            email = _clean(row.get("email", ""))
            if not email or "@" not in email:
                continue
            name = _clean(row.get("name", ""))
            org  = _clean(row.get("org", ""))
            custom_fields = {
                k: v for k, v in row.items()
                if k not in ("email", "name", "org") and _clean(v)
            }
            validation = await validate_email(email)
            contacts.append({
                "email": email,
                "name": name,
                "org": org,
                "custom_fields": custom_fields,
                "email_status": validation["status"]
            })
        return contacts
    except Exception as e:
        raise ValueError(f"Failed to import from Google Sheets: {str(e)}")

async def save_contact_list(db, user_id: str, name: str, contacts: list[dict]):
    list_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    contact_list = {
        "_id": list_id,
        "user_id": user_id,
        "name": name,
        "description": None,
        "created_at": now
    }
    
    await db.contact_lists.insert_one(contact_list)
    
    if contacts:
        db_contacts = []
        for c in contacts:
            c_doc = dict(c)
            c_doc["_id"] = str(uuid.uuid4())
            c_doc["list_id"] = list_id
            c_doc["user_id"] = user_id
            db_contacts.append(c_doc)
            
        await db.contacts.insert_many(db_contacts)
        
    return contact_list

async def get_contact_lists(db, user_id: str):
    cursor = db.contact_lists.find({"user_id": user_id})
    lists = await cursor.to_list(length=1000)
    for l in lists:
        l["total_contacts"] = await db.contacts.count_documents({"list_id": l["_id"]})
    return lists

async def get_contact_list(db, user_id: str, list_id: str):
    return await db.contact_lists.find_one({"_id": list_id, "user_id": user_id})

async def update_contact(db, user_id: str, contact_id: str, data: dict):
    # filter out _id, list_id, user_id
    update_data = {k: v for k, v in data.items() if k not in ['_id', 'list_id', 'user_id']}
    result = await db.contacts.find_one_and_update(
        {"_id": contact_id, "user_id": user_id},
        {"$set": update_data},
        return_document=True
    )
    return result

async def delete_contact_list(db, user_id: str, list_id: str) -> bool:
    result = await db.contact_lists.delete_one({"_id": list_id, "user_id": user_id})
    if result.deleted_count > 0:
        await db.contacts.delete_many({"list_id": list_id, "user_id": user_id})
        return True
    return False
