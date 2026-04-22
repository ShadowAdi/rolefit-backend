"""
Advanced Test Runner with Configuration
Provides command-line interface for flexible test execution
"""

import argparse
import json
from test_resume_generation import ResumeGenerationTester


def run_with_args():
    """Parse command-line arguments and run tests"""
    parser = argparse.ArgumentParser(
        description="Resume Generation Test Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_runner.py                          # Run with defaults
  python test_runner.py --users 5                # Test with 5 users
  python test_runner.py --url http://localhost:8000/api/v1
  python test_runner.py --users 2 --export results.json
        """,
    )

    parser.add_argument(
        "--users",
        type=int,
        default=3,
        help="Number of test users to create (default: 3)",
    )

    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:8000/api/v1",
        help="Base URL of the API (default: http://localhost:8000/api/v1)",
    )

    parser.add_argument(
        "--export", type=str, help="Export results to JSON file (optional)"
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Run tests
    tester = ResumeGenerationTester(base_url=args.url)

    # Update global users count
    import test_resume_generation

    test_resume_generation.USERS_COUNT = args.users

    # Run the complete flow
    tester.run_complete_flow()

    # Export results if requested
    if args.export:
        with open(args.export, "w") as f:
            json.dump(tester.test_results, f, indent=2)
        print(f"\n📊 Results exported to: {args.export}")

    return tester.test_results


if __name__ == "__main__":
    run_with_args()
