#!/usr/bin/env python3
"""
Debug script to test job description creation
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

# Test data
email = f"testuser_{int(time.time() * 1000)}@testdomain.com"
password = "TestPassword123!"

print("=" * 60)
print("DEBUG: Job Description Creation Test")
print("=" * 60)

# Step 1: Register user
print("\n1. Registering user...")
try:
    response = requests.post(
        f"{BASE_URL}/user/register",
        json={"email": email, "password": password}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code != 201:
        print(f"   Response: {response.text}")
        exit(1)
    
    user_data = response.json()
    user_id = user_data.get("data", {}).get("id")
    print(f"   User ID: {user_id}")
except Exception as e:
    print(f"   ERROR: {e}")
    exit(1)

# Step 2: Login
print("\n2. Logging in...")
try:
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": email, "password": password}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Response: {response.text}")
        exit(1)
    
    access_token = response.json().get("access_token")
    print(f"   Token: {access_token[:20]}...")
except Exception as e:
    print(f"   ERROR: {e}")
    exit(1)

# Step 3: Create job description
print("\n3. Creating job description...")
headers = {"Authorization": f"Bearer {access_token}"}
payload = {
    "role_name": "Senior Software Engineer",
    "company": "Tech Company",
    "raw_jd": "Looking for experienced software engineer with 5+ years experience in Python and microservices.",
    "required_skills": ["Python", "FastAPI", "PostgreSQL"],
    "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
    "role_type": "Full-time",
    "location": "Remote",
    "experience_required": "5+ years"
}

print(f"   Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(
        f"{BASE_URL}/job-descriptions/",
        json=payload,
        headers=headers
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:500]}")
    
    if response.status_code == 201:
        print("   ✓ SUCCESS!")
    else:
        print("   ✗ FAILED!")
        
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
