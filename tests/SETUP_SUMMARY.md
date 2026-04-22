# Resume Generation Test Suite - Complete Documentation

## 📦 What's Been Created

A comprehensive test suite for the Rolefit Backend API with the following components:

### Test Files

1. **test_resume_generation.py** - Main test script
   - Creates test users with unique credentials
   - Registers and authenticates users
   - Creates profiles with sample data
   - Adds multiple work experiences
   - Generates resume text via the content API
   - Provides detailed reporting and error handling

2. **test_runner.py** - Advanced CLI wrapper
   - Command-line argument parsing
   - Flexible configuration options
   - JSON result export capability
   - Verbose logging option

3. **health_check.py** - API health verification
   - Checks server connectivity
   - Verifies endpoint availability
   - Helpful diagnostic information
   - Run before full test suite

4. **run_tests.bat** - Windows batch script
   - Interactive menu system
   - Automatic environment setup
   - Dependency installation
   - Easy one-click testing

### Documentation Files

1. **README.md** - Comprehensive documentation
   - Overview and features
   - Setup requirements
   - Configuration options
   - Running instructions
   - Troubleshooting guide

2. **QUICKSTART.md** - Quick start guide
   - 3-step getting started
   - Output explanation
   - Customization examples
   - Common issues and solutions

3. **test_requirements.txt** - Python dependencies
   - requests (HTTP client)
   - pytest (testing framework)
   - pytest-asyncio (async testing)

## 🎯 Test Flow

```
START
  ↓
Generate 3 Test Users (configurable)
  ├─ testuser0_{timestamp}@testdomain.com
  ├─ testuser1_{timestamp}@testdomain.com
  └─ testuser2_{timestamp}@testdomain.com
  ↓
For Each User:
  ├─ Register User
  │   └─ POST /user/register
  ├─ Login User
  │   └─ POST /auth/login (get token)
  ├─ Create Profile
  │   └─ POST /profile/
  ├─ Add Experience 1
  │   └─ POST /experience/ (Senior SWE at Tech Corp)
  ├─ Add Experience 2
  │   └─ POST /experience/ (Full Stack Dev at StartUp)
  ├─ Create Job Description
  │   └─ POST /job-descriptions/
  └─ Generate Resume
      └─ POST /content/{jobId}
  ↓
Display Results Summary
  ├─ Users Created Count
  ├─ Profiles Created Count
  ├─ Experiences Created Count
  ├─ Resumes Generated Count
  └─ Failed Operations (if any)
  ↓
END
```

## 🚀 Quick Start

### Windows Users
```bash
cd c:\Users\lenovo\Desktop\rolefit\rolefit-backend\tests
run_tests.bat
```

### All Users
```bash
cd c:\Users\lenovo\Desktop\rolefit\rolefit-backend

# Check health first
python tests/health_check.py

# Run tests
python tests/test_resume_generation.py
```

### Advanced Options
```bash
# Test with 5 users
python tests/test_runner.py --users 5

# Custom URL
python tests/test_runner.py --url http://localhost:8001/api/v1

# Export results
python tests/test_runner.py --users 5 --export results.json

# Verbose output
python tests/test_runner.py --verbose
```

## 📊 Sample Test Output

```
======================================================================
RESUME GENERATION TEST - COMPLETE FLOW
======================================================================

📋 Step 1: Generating test users...
Generated 3 test user credentials

👤 Processing User 1/3
----------------------------------------------------------------------
✓ User registered: testuser0_1234567890@testdomain.com (ID: 550e8400...)
✓ User logged in: testuser0_1234567890@testdomain.com
✓ Profile created for testuser0_1234567890@testdomain.com (Profile ID: 6ba7b810...)
  
  Adding experience data...
✓ Experience created: Senior Software Engineer at Tech Corp
✓ Experience created: Full Stack Developer at StartUp Inc
  
  Creating job description...
✓ Job description created
  
  Generating resume text...
✓ Resume generated successfully!
  Resume Preview: Experienced Senior Software Engineer with a demonstrated...

👤 Processing User 2/3
----------------------------------------------------------------------
[Similar output for user 2]

👤 Processing User 3/3
----------------------------------------------------------------------
[Similar output for user 3]

======================================================================
TEST SUMMARY
======================================================================
Users Created:       3/3
Profiles Created:    3/3
Experiences Created: 6
Resumes Generated:   3

✓ All operations completed successfully!
======================================================================
```

## 🔧 Configuration

### Default Settings
```python
BASE_URL = "http://localhost:8000/api/v1"
USERS_COUNT = 3
```

### Customize Test Data
Edit test_resume_generation.py to change:
- User credentials pattern
- Profile information
- Experience descriptions
- Job description details

### Change API Endpoint
```bash
python tests/test_runner.py --url http://your-server:port/api/v1
```

## 📋 Test Data Created

### Users
- **Email Pattern**: `testuser{n}_{timestamp}@testdomain.com`
- **Password**: `TestPassword123!`
- **Auto-generated**: Unique for each run

### Profile
- **Full Name**: Test User {id}
- **Headline**: Software Engineer | Full Stack Developer
- **Summary**: Passionate developer with experience in building scalable applications.
- **Links**: GitHub and LinkedIn profiles

### Experiences
1. **Senior Software Engineer** - Tech Corp (2021-2023)
   - Tech: Python, FastAPI, PostgreSQL, Docker, Kubernetes

2. **Full Stack Developer** - StartUp Inc (2019-2020)
   - Tech: JavaScript, React, Node.js, MongoDB, AWS

3. **Junior Developer** - Digital Agency (2018-2019)
   - Tech: HTML, CSS, JavaScript, PHP, MySQL

## ✅ Success Indicators

Your tests are working when:
- ✓ All user registrations succeed
- ✓ All authentications complete
- ✓ All profiles are created
- ✓ All experiences are added
- ✓ Resume text is generated
- ✓ Test summary shows 0 failed operations

## ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| "Cannot connect to server" | Start backend: `python -m uvicorn main:app --reload` |
| "Email already exists" | The script auto-generates unique emails; try again |
| "Invalid token" | Ensure JWT is properly configured |
| "Resume not generated" | Verify experiences are created and job ID is valid |
| "Profile already exists" | Each user should only have one profile |

## 📁 File Structure

```
tests/
├── __init__.py                      # Module init
├── test_resume_generation.py        # Main test script (650+ lines)
├── test_runner.py                   # CLI wrapper (~100 lines)
├── health_check.py                  # Health verification (~200 lines)
├── run_tests.bat                    # Windows batch script
├── test_requirements.txt            # Python dependencies
├── README.md                        # Full documentation
├── QUICKSTART.md                    # Quick start guide
└── SETUP_SUMMARY.md                 # This file
```

## 🎓 What This Tests

1. **User Management**
   - User registration with email/password
   - User authentication and token generation
   - JWT token handling

2. **Profile Management**
   - Profile creation with user data
   - Profile association with user
   - Data persistence

3. **Experience Management**
   - Multiple experience creation per user
   - Experience data validation
   - Complex data structures (arrays, dates)

4. **Resume Generation**
   - Content API functionality
   - Resume text generation from experiences
   - Job matching algorithm

## 💾 Data Persistence

**Important**: Test data is persisted in your database
- Test users remain after tests complete
- Profiles and experiences are saved
- Data can be manually deleted if needed

To add cleanup:
```python
# Add this to test_resume_generation.py
def cleanup_test_data(user_ids: list):
    # Delete test users from database
    for user_id in user_ids:
        # DELETE /user/{user_id}
        pass
```

## 🔐 Security Notes

- Test script uses hardcoded test data (OK for testing only)
- Never use real passwords in test data
- The email pattern ensures uniqueness
- Tokens are generated fresh for each test run

## 📈 Performance Metrics

The script provides timing information (you can enhance it):
- Registration time per user
- Profile creation time
- Experience creation time
- Resume generation time

To add timing:
```python
import time
start = time.time()
# operation
end = time.time()
print(f"Operation took {end-start:.2f}s")
```

## 🔄 Workflow Validation

The tests validate this complete workflow:
```
User Creates Account → Creates Profile → Adds Experience → 
Gets Job Description → System Generates Resume → Success!
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Requests Library](https://requests.readthedocs.io/)
- [JWT Authentication](https://jwt.io/)
- [SQLAlchemy ORM](https://www.sqlalchemy.org/)

## 📞 Support

If tests fail:
1. Check error message in output
2. Review backend logs
3. Run health check
4. Verify database connectivity
5. Check environment variables

## ✨ Features

- ✅ Automated user creation with unique credentials
- ✅ Complete workflow testing (register → login → create profile → add experience → generate resume)
- ✅ Multiple user support (test scalability)
- ✅ Comprehensive error reporting
- ✅ CLI with flexible options
- ✅ Health check utility
- ✅ JSON result export
- ✅ Windows batch script for easy execution
- ✅ Detailed documentation
- ✅ Professional logging and output

---

**Created**: April 23, 2026  
**Version**: 1.0  
**Status**: Ready for Use ✅
