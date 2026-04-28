import requests
import time

BASE_URL = "http://127.0.0.1:8000/api"

def run_diagnostics():
    report = []
    def log(msg, status="INFO"):
        report.append(f"[{status}] {msg}")
        print(f"[{status}] {msg}")

    # 1. Health check
    try:
        r = requests.get("http://127.0.0.1:8000/health")
        if r.status_code == 200:
            log("Health check passed", "PASS")
        else:
            log(f"Health check failed: {r.status_code}", "FAIL")
    except Exception as e:
        log(f"Health check exception: {e}", "FAIL")

    # 2. Register / Login
    email = f"test_{int(time.time())}@example.com"
    password = "password123"
    token = None
    user_id = None
    try:
        r = requests.post(f"{BASE_URL}/auth/register", json={
            "name": "Test User",
            "email": email,
            "password": password
        })
        if r.status_code == 200:
            log("User registration passed", "PASS")
            token = r.json().get("access_token")
            user_id = r.json().get("user", {}).get("id")
        else:
            log(f"User registration failed: {r.status_code} {r.text}", "FAIL")
    except Exception as e:
        log(f"User registration exception: {e}", "FAIL")

    if not token:
        try:
            r = requests.post(f"{BASE_URL}/auth/login", json={
                "email": email,
                "password": password
            })
            if r.status_code == 200:
                log("User login passed", "PASS")
                token = r.json().get("access_token")
                user_id = r.json().get("user", {}).get("id")
            else:
                log(f"User login failed: {r.status_code} {r.text}", "FAIL")
        except Exception as e:
            log(f"User login exception: {e}", "FAIL")

    if not token:
        log("Cannot proceed with authenticated tests without token", "ERROR")
        return "\n".join(report)

    headers = {"Authorization": f"Bearer {token}"}

    # 3. Settings
    try:
        r = requests.post(f"{BASE_URL}/settings", headers=headers, json={
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
            "smtp_user": "test@example.com",
            "smtp_password": "password123",
            "use_tls": True
        })
        if r.status_code == 200:
            log("Update settings passed", "PASS")
        else:
            log(f"Update settings failed: {r.status_code} {r.text}", "FAIL")
    except Exception as e:
        log(f"Settings exception: {e}", "FAIL")

    # 4. Contacts
    list_id = None
    try:
        r = requests.post(f"{BASE_URL}/contacts/lists", headers=headers, json={
            "name": "Test List",
            "description": "A test list"
        })
        if r.status_code == 200:
            log("Create contact list passed", "PASS")
            list_id = r.json().get("_id")
        else:
            log(f"Create contact list failed: {r.status_code} {r.text}", "FAIL")
    except Exception as e:
        log(f"Contact list exception: {e}", "FAIL")

    if list_id:
        try:
            r = requests.post(f"{BASE_URL}/contacts/{list_id}/contacts", headers=headers, json={
                "email": "contact@example.com",
                "name": "Contact One"
            })
            if r.status_code == 200:
                log("Add contact passed", "PASS")
            else:
                log(f"Add contact failed: {r.status_code} {r.text}", "FAIL")
        except Exception as e:
            log(f"Add contact exception: {e}", "FAIL")

    # 5. Templates
    template_id = None
    try:
        r = requests.post(f"{BASE_URL}/template", headers=headers, json={
            "name": "Test Template",
            "subject": "Hello {first_name}",
            "html_body": "<p>Hello {first_name}, how are you?</p>"
        })
        if r.status_code == 200:
            log("Create template passed", "PASS")
            template_id = r.json().get("_id")
        else:
            log(f"Create template failed: {r.status_code} {r.text}", "FAIL")
    except Exception as e:
        log(f"Template exception: {e}", "FAIL")

    # 6. Mail Job
    if list_id and template_id:
        try:
            r = requests.post(f"{BASE_URL}/mail/jobs", headers=headers, json={
                "template_id": template_id,
                "contact_list_id": list_id
            })
            if r.status_code == 200:
                log("Create mail job passed", "PASS")
                job_id = r.json().get("job_id")
                
                # Check status
                r_status = requests.get(f"{BASE_URL}/mail/jobs/{job_id}/status", headers=headers)
                if r_status.status_code == 200:
                    log("Get mail job status passed", "PASS")
                else:
                    log(f"Get mail job status failed: {r_status.status_code}", "FAIL")
            else:
                log(f"Create mail job failed: {r.status_code} {r.text}", "FAIL")
        except Exception as e:
            log(f"Mail job exception: {e}", "FAIL")

    # Admin Login
    admin_token = None
    try:
        r = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "jiteshbawaskar05@gmail.com",
            "password": "Jitesh001@"
        })
        if r.status_code == 200:
            log("Admin login passed", "PASS")
            admin_token = r.json().get("access_token")
        else:
            log(f"Admin login failed: {r.status_code} {r.text}", "FAIL")
    except Exception as e:
        log(f"Admin login exception: {e}", "FAIL")

    if admin_token:
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        try:
            r = requests.get(f"{BASE_URL}/admin/stats", headers=admin_headers)
            if r.status_code == 200:
                log("Admin stats passed", "PASS")
            else:
                log(f"Admin stats failed: {r.status_code} {r.text}", "FAIL")
        except Exception as e:
            log(f"Admin stats exception: {e}", "FAIL")

    with open("report.txt", "w") as f:
        f.write("\n".join(report))

if __name__ == '__main__':
    run_diagnostics()
