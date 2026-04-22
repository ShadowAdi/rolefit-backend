"""
Test script for Resume Generation Flow
This script tests the complete flow of:
1. Creating users with email and password
2. Creating profiles for users
3. Adding experience data
4. Generating resume text via content API
"""

import requests
import json
import time
from typing import Optional, Dict, Any
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
USERS_COUNT = 3  # Number of test users to create


class TestUser:
    """Helper class to store user test data"""

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.user_id: Optional[str] = None
        self.access_token: Optional[str] = None
        self.profile_id: Optional[str] = None
        self.experience_ids: list = []
        self.job_ids: list = []


class ResumeGenerationTester:
    """Main test class for resume generation flow"""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.users: list[TestUser] = []
        self.test_results = {
            "users_created": 0,
            "profiles_created": 0,
            "experiences_created": 0,
            "resume_generated": 0,
            "failed_operations": [],
        }

    def generate_test_users(self, count: int) -> list[TestUser]:
        """Generate test user credentials"""
        users = []
        for i in range(count):
            timestamp = int(time.time() * 1000)
            email = f"testuser{i}_{timestamp}@testdomain.com"
            password = "TestPassword123!"
            users.append(TestUser(email=email, password=password))
        return users

    def register_user(self, user: TestUser) -> bool:
        """Register a new user"""
        try:
            url = f"{self.base_url}/user/register"
            payload = {"email": user.email, "password": user.password}

            response = requests.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            user.user_id = data.get("data", {}).get("id")

            print(f"✓ User registered: {user.email} (ID: {user.user_id})")
            self.test_results["users_created"] += 1
            return True

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to register user {user.email}: {str(e)}"
            print(f"✗ {error_msg}")
            self.test_results["failed_operations"].append(error_msg)
            return False

    def login_user(self, user: TestUser) -> bool:
        """Login user and get access token"""
        try:
            url = f"{self.base_url}/auth/login"
            payload = {"email": user.email, "password": user.password}

            response = requests.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            user.access_token = data.get("access_token")

            print(f"✓ User logged in: {user.email}")
            return True

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to login user {user.email}: {str(e)}"
            print(f"✗ {error_msg}")
            self.test_results["failed_operations"].append(error_msg)
            return False

    def get_headers(self, user: TestUser) -> Dict[str, str]:
        """Get authorization headers for a user"""
        return {
            "Authorization": f"Bearer {user.access_token}",
            "Content-Type": "application/json",
        }

    def create_profile(self, user: TestUser) -> bool:
        """Create profile for user"""
        try:
            url = f"{self.base_url}/profile/"
            headers = self.get_headers(user)

            payload = {
                "full_name": f"Test User {user.user_id[:8]}",
                "headline": "Software Engineer | Full Stack Developer",
                "summary": "Passionate developer with experience in building scalable applications.",
                "resume_link": "https://example.com/resume.pdf",
                "cover_letter_link": "https://example.com/cover_letter.pdf",
                "links": {
                    "github": "https://github.com/testuser",
                    "linkedin": "https://linkedin.com/in/testuser",
                },
            }

            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()
            user.profile_id = data.get("id")

            print(f"✓ Profile created for {user.email} (Profile ID: {user.profile_id})")
            self.test_results["profiles_created"] += 1
            return True

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to create profile for {user.email}: {str(e)}"
            print(f"✗ {error_msg}")
            self.test_results["failed_operations"].append(error_msg)
            return False

    def create_experience(self, user: TestUser, experience_num: int = 1) -> bool:
        """Create experience for user"""
        try:
            url = f"{self.base_url}/experience/"
            headers = self.get_headers(user)

            experiences = [
                {
                    "company_name": "Tech Corp",
                    "role": "Senior Software Engineer",
                    "description": "Led development of microservices architecture. Mentored junior developers and conducted code reviews.",
                    "techStack": [
                        "Python",
                        "FastAPI",
                        "PostgreSQL",
                        "Docker",
                        "Kubernetes",
                    ],
                    "employment_type": "Full-time",
                    "location_type": "Remote",
                    "location_details": "USA",
                    "start_month": 1,
                    "start_year": 2021,
                    "end_month": 6,
                    "end_year": 2023,
                    "priority": 1,
                },
                {
                    "company_name": "StartUp Inc",
                    "role": "Full Stack Developer",
                    "description": "Developed and deployed full-stack web applications. Implemented REST APIs and responsive UI components.",
                    "techStack": ["JavaScript", "React", "Node.js", "MongoDB", "AWS"],
                    "employment_type": "Full-time",
                    "location_type": "Hybrid",
                    "location_details": "San Francisco, CA",
                    "start_month": 6,
                    "start_year": 2019,
                    "end_month": 12,
                    "end_year": 2020,
                    "priority": 2,
                },
                {
                    "company_name": "Digital Agency",
                    "role": "Junior Developer",
                    "description": "Built responsive websites and web applications. Collaborated with designers and product managers.",
                    "techStack": ["HTML", "CSS", "JavaScript", "PHP", "MySQL"],
                    "employment_type": "Full-time",
                    "location_type": "On-site",
                    "location_details": "New York, NY",
                    "start_month": 3,
                    "start_year": 2018,
                    "end_month": 5,
                    "end_year": 2019,
                    "priority": 3,
                },
            ]

            if experience_num - 1 >= len(experiences):
                experience_num = len(experiences)

            payload = experiences[experience_num - 1]

            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()
            experience_id = data.get("id")
            user.experience_ids.append(experience_id)

            print(
                f"✓ Experience created: {payload['role']} at {payload['company_name']}"
            )
            self.test_results["experiences_created"] += 1
            return True

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to create experience for {user.email}: {str(e)}"
            print(f"✗ {error_msg}")
            self.test_results["failed_operations"].append(error_msg)
            return False

    def create_job_description(self, user: TestUser) -> Optional[str]:
        """Create a job description for testing"""
        try:
            # This is a simplified job description creation
            # You may need to adjust based on your actual job description endpoint
            url = f"{self.base_url}/job-descriptions/"
            headers = self.get_headers(user)

            payload = {
                "title": "Senior Software Engineer",
                "company": "Tech Company",
                "description": "Looking for experienced software engineer with Python and microservices experience.",
                "requirements": [
                    "5+ years experience",
                    "Python",
                    "FastAPI",
                    "PostgreSQL",
                ],
            }

            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()
            job_id = data.get("id")
            return job_id

        except requests.exceptions.RequestException as e:
            print(f"Note: Job description creation may not be implemented: {str(e)}")
            return None

    def generate_resume_text(self, user: TestUser, job_id: str) -> bool:
        """Generate resume text for a user and job"""
        try:
            url = f"{self.base_url}/content/{job_id}"
            headers = self.get_headers(user)

            response = requests.post(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            resume_text = data.get("resume_text", "")

            print(f"✓ Resume generated successfully!")
            print(f"  Resume Preview: {resume_text[:100]}...")
            self.test_results["resume_generated"] += 1
            return True

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to generate resume for {user.email}: {str(e)}"
            print(f"✗ {error_msg}")
            self.test_results["failed_operations"].append(error_msg)
            return False

    def run_complete_flow(self):
        """Run the complete test flow"""
        print("\n" + "=" * 70)
        print("RESUME GENERATION TEST - COMPLETE FLOW")
        print("=" * 70)

        # Generate test users
        print("\n📋 Step 1: Generating test users...")
        self.users = self.generate_test_users(USERS_COUNT)
        print(f"Generated {len(self.users)} test user credentials\n")

        # Register and process each user
        for idx, user in enumerate(self.users, 1):
            print(f"\n👤 Processing User {idx}/{len(self.users)}")
            print("-" * 70)

            # Register
            if not self.register_user(user):
                continue

            # Login
            if not self.login_user(user):
                continue

            # Create Profile
            if not self.create_profile(user):
                continue

            # Add Multiple Experiences
            print(f"\n  Adding experience data...")
            for exp_num in range(1, 3):  # Add 2 experiences per user
                self.create_experience(user, exp_num)

            # Try to create job description
            print(f"\n  Creating job description...")
            job_id = self.create_job_description(user)

            if job_id:
                user.job_ids.append(job_id)
                # Try to generate resume
                print(f"\n  Generating resume text...")
                self.generate_resume_text(user, job_id)
            else:
                print(f"  ⓘ Skipping resume generation (no job ID)")

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(
            f"Users Created:       {self.test_results['users_created']}/{len(self.users)}"
        )
        print(
            f"Profiles Created:    {self.test_results['profiles_created']}/{len(self.users)}"
        )
        print(f"Experiences Created: {self.test_results['experiences_created']}")
        print(f"Resumes Generated:   {self.test_results['resume_generated']}")

        if self.test_results["failed_operations"]:
            print(
                f"\n⚠️  Failed Operations ({len(self.test_results['failed_operations'])}):"
            )
            for operation in self.test_results["failed_operations"]:
                print(f"  - {operation}")
        else:
            print(f"\n✓ All operations completed successfully!")

        print("\n" + "=" * 70)

        return self.test_results


def main():
    """Main test runner"""
    print("\n🚀 Starting Resume Generation Test Suite\n")

    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}")
        print(f"✓ Server is running at {BASE_URL}")
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to server at {BASE_URL}")
        print(f"  Make sure the backend server is running:")
        print(f"  cd rolefit-backend && python -m uvicorn main:app --reload")
        return

    # Run tests
    tester = ResumeGenerationTester(BASE_URL)
    tester.run_complete_flow()


if __name__ == "__main__":
    main()
