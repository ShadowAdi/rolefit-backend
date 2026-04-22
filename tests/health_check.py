"""
Quick API Health Check and Endpoint Verification
Use this to verify API endpoints are accessible before running full tests
"""

import requests
import json
from typing import Dict, Tuple


class APIHealthChecker:
    """Check API health and endpoint availability"""

    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.base_domain = base_url.replace("/api/v1", "")
        self.health_results = {}

    def check_server_health(self) -> bool:
        """Check if server is running"""
        try:
            response = requests.get(f"{self.base_domain}/", timeout=5)
            return response.status_code < 500
        except requests.exceptions.ConnectionError:
            return False
        except Exception:
            return False

    def check_endpoint(
        self, method: str, endpoint: str, headers: Dict = None
    ) -> Tuple[bool, int, str]:
        """Check if an endpoint is accessible"""
        try:
            url = f"{self.base_url}{endpoint}"
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=5)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json={}, timeout=5)
            else:
                return False, 0, "Unsupported method"

            # 401 and 422 are OK - means endpoint exists
            if response.status_code in [200, 201, 400, 401, 404, 422]:
                return True, response.status_code, "OK"
            else:
                return False, response.status_code, response.text[:100]

        except requests.exceptions.Timeout:
            return False, 0, "Timeout"
        except requests.exceptions.ConnectionError:
            return False, 0, "Connection refused"
        except Exception as e:
            return False, 0, str(e)[:100]

    def run_health_check(self):
        """Run complete health check"""
        print("\n" + "=" * 70)
        print("API HEALTH CHECK")
        print("=" * 70)

        # Check server
        print(f"\nChecking server at: {self.base_domain}")
        if self.check_server_health():
            print("✓ Server is running")
        else:
            print("✗ Server is not responding")
            print("  Start the server with:")
            print("  cd rolefit-backend && python -m uvicorn main:app --reload")
            return False

        # Check endpoints
        endpoints = [
            ("POST", "/user/register", "User Registration"),
            ("POST", "/auth/login", "User Login"),
            ("POST", "/profile/", "Profile Creation"),
            ("GET", "/profile/", "Profile Retrieval"),
            ("POST", "/experience/", "Experience Creation"),
            ("GET", "/experience/", "Experience Retrieval"),
            ("POST", "/job-descriptions/", "Job Description Creation"),
            ("POST", "/content/{jobId}", "Content/Resume Generation"),
        ]

        print(f"\n" + "-" * 70)
        print("Endpoint Status:")
        print("-" * 70)

        all_accessible = True
        for method, endpoint, description in endpoints:
            accessible, status_code, message = self.check_endpoint(method, endpoint)

            symbol = "✓" if accessible else "✗"
            status = f"[{status_code}]" if status_code else "[N/A]"

            print(f"{symbol} {description:30} {method:6} {endpoint:25} {status}")

            if (
                not accessible and status_code != 401
            ):  # 401 is OK for protected endpoints
                all_accessible = False

        print("\n" + "=" * 70)
        if all_accessible:
            print("✓ All endpoints are accessible!")
            print("\nYou can now run the test suite:")
            print("  python tests/test_resume_generation.py")
        else:
            print("⚠️  Some endpoints may have issues")
            print("Check the API server logs for details")

        print("=" * 70 + "\n")

        return all_accessible


def main():
    """Run health check"""
    import sys

    # Accept URL as argument
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/api/v1"

    checker = APIHealthChecker(base_url=url)
    success = checker.run_health_check()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
