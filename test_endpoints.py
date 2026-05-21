import requests
import sys

BASE = "http://localhost:8000/api/v1"

print("--- REGISTER ---")
r = requests.post(f"{BASE}/auth/register", json={
    "email": "test1234@esi-sba.dz",
    "password": "Test1234!",
    "full_name": "Test User",
    "username": "testuser1234"
})
print("REGISTER:", r.status_code, r.json())
sys.stdout.flush()

code = input("Enter verification code from terminal: ")
r = requests.post(f"{BASE}/auth/verify-email", json={
    "email": "test1234@esi-sba.dz",
    "code": code
})
print("VERIFY:", r.status_code, r.json())
token = r.json().get("access_token")

headers = {"Authorization": f"Bearer {token}"}

print("--- GET CURRENT USER ---")
r = requests.get(f"{BASE}/auth/me", headers=headers)
print("ME:", r.status_code, r.json())

print("--- CREATE PROJECT ---")
r = requests.post(f"{BASE}/projects/", headers=headers, json={
    "title": "Test Project",
    "description": "A test project",
    "required_skill_ids": [],
    "max_members": 5
})
print("CREATE PROJECT:", r.status_code, r.json())

print("--- LIST PROJECTS ---")
r = requests.get(f"{BASE}/projects/", headers=headers)
print("LIST PROJECTS:", r.status_code, r.json())

print("--- MY TEAMS ---")
r = requests.get(f"{BASE}/projects/my-teams", headers=headers)
print("MY TEAMS:", r.status_code, r.json())

print("--- TASKS DASHBOARD ---")
r = requests.get(f"{BASE}/tasks/dashboard", headers=headers)
print("TASKS DASHBOARD:", r.status_code, r.json())

print("--- NOTIFICATIONS ---")
r = requests.get(f"{BASE}/notifications/", headers=headers)
print("NOTIFICATIONS:", r.status_code, r.json())
