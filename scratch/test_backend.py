import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    print("Testing /health...")
    r = requests.get(f"{BASE_URL}/health")
    print(f"Health Response: {r.status_code} - {r.json()}")

def test_login():
    print("\nTesting login...")
    login_data = {
        "email": "jiteshbawaskar05@gmail.com",
        "password": "Jitesh001@"
    }
    r = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print(f"Login Response: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print("Login Success!")
        print(f"Access Token: {data['access_token'][:20]}...")
        return data['access_token']
    else:
        print(f"Login Failed: {r.text}")
        return None

def test_me(token):
    print("\nTesting /api/auth/me...")
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    print(f"Me Response: {r.status_code} - {r.json()}")

if __name__ == "__main__":
    test_health()
    token = test_login()
    if token:
        test_me(token)
