# Quick Start Guide - Resume Generation Tests

## 🚀 Get Started in 3 Steps

### Step 1: Start the Backend Server

```bash
cd c:\Users\lenovo\Desktop\rolefit\rolefit-backend

# Activate virtual environment (if using venv)
env\Scripts\activate

# Start the server
python -m uvicorn main:app --reload
```

The server should start at `http://localhost:8000`

### Step 2: Run Health Check (Optional but Recommended)

```bash
cd c:\Users\lenovo\Desktop\rolefit\rolefit-backend
python tests/health_check.py
```

This verifies all required endpoints are accessible.

### Step 3: Run the Test Suite

```bash
cd c:\Users\lenovo\Desktop\rolefit\rolefit-backend
python tests/test_resume_generation.py
```

Or with the test runner for more options:

```bash
python tests/test_runner.py --users 5 --export results.json
```

## 📊 Understanding the Output

### Success Example
```
✓ User registered: testuser0_1234567890@testdomain.com
✓ User logged in: testuser0_1234567890@testdomain.com
✓ Profile created for testuser0_1234567890@testdomain.com
✓ Experience created: Senior Software Engineer at Tech Corp
✓ Resume generated successfully!
```

### Failure Example
```
✗ Failed to register user: User email already exists
⚠️  Check the server logs for more details
```

## 🎯 Test Flow Overview

```
1. Generate Test Users
   ↓
2. Register Users (email + password)
   ↓
3. Login (get access token)
   ↓
4. Create Profile (full_name, headline, summary)
   ↓
5. Add Experiences (company, role, description, dates)
   ↓
6. Create Job Description
   ↓
7. Generate Resume Text
   ↓
8. Display Results
```

## 📋 What Gets Created

### Test Users
- Email: `testuser{n}_{timestamp}@testdomain.com`
- Password: `TestPassword123!`
- Auto-generated unique credentials for each run

### Profiles
- Full Name: "Test User {id}"
- Headline: "Software Engineer | Full Stack Developer"
- Summary: Professional bio
- Links: GitHub and LinkedIn profiles

### Experiences (2 per user)
1. **Senior Software Engineer** at Tech Corp
   - Tech Stack: Python, FastAPI, PostgreSQL, Docker, Kubernetes
   - Duration: 2021-2023

2. **Full Stack Developer** at StartUp Inc
   - Tech Stack: JavaScript, React, Node.js, MongoDB, AWS
   - Duration: 2019-2020

## 🔧 Customization Options

### Change Number of Users
Edit `test_resume_generation.py`:
```python
USERS_COUNT = 5  # Create 5 users instead of 3
```

Or use command line:
```bash
python tests/test_runner.py --users 5
```

### Change API URL
If your server is on a different port:
```bash
python tests/test_runner.py --url http://localhost:8001/api/v1
```

### Export Results
Save test results to JSON:
```bash
python tests/test_runner.py --export results.json
```

Results file format:
```json
{
  "users_created": 3,
  "profiles_created": 3,
  "experiences_created": 6,
  "resume_generated": 3,
  "failed_operations": []
}
```

## 🐛 Troubleshooting

### Issue: "Cannot connect to server"
**Solution:** Make sure the backend server is running:
```bash
python -m uvicorn main:app --reload
```

### Issue: "User already exists"
**Solution:** The script generates unique emails with timestamps, but if you run it very quickly, the timestamp might be identical. Wait a second and try again.

### Issue: "Invalid email format"
**Solution:** Check that email validation is working in your User model. The script uses valid email formats.

### Issue: "Resume generation failed"
**Solution:** 
1. Verify experiences have been created
2. Check the content API is working
3. Review backend logs for error messages

### Issue: "Token expired"
**Solution:** The test script handles token creation right before use, so this should not happen. If it does, check your JWT configuration.

## 📚 File Structure

```
tests/
├── __init__.py                      # Module initialization
├── README.md                        # Detailed documentation
├── QUICKSTART.md                    # This file
├── test_resume_generation.py        # Main test script
├── test_runner.py                   # CLI wrapper with options
└── health_check.py                  # API health verification
```

## 💡 Tips & Best Practices

1. **Run Health Check First**
   - Always run `health_check.py` before the full test suite
   - Saves time debugging connection issues

2. **Start Small**
   - Test with 1-2 users first: `--users 1`
   - Verify the flow works before scaling up

3. **Review Logs**
   - Keep the backend terminal open to see logs
   - This helps identify API errors quickly

4. **Test Data Persistence**
   - Test data remains in your database
   - Good for manual verification
   - Delete test users if needed for cleanup

5. **Performance Testing**
   - Run with `--users 10` or more to test performance
   - Monitor API response times in the output

## 🎓 Learning Resources

**Test Script Concepts:**
- User Registration and Authentication
- Token-based Authorization (Bearer tokens)
- REST API requests (POST, GET)
- JSON payload construction
- Error handling and reporting

**Backend Integration:**
- FastAPI endpoint testing
- Database operations verification
- API response validation
- User workflow testing

## ✅ Success Criteria

Your test is successful when you see:
- ✓ All users created and authenticated
- ✓ All profiles created successfully
- ✓ All experiences added
- ✓ Resume text generated and displayed
- ✓ Test summary shows 0 failed operations

## 📞 Need Help?

If tests fail:
1. Check the error message in the test output
2. Review backend logs for detailed errors
3. Run health check to verify endpoints
4. Verify database is properly initialized
5. Check that all required environment variables are set

---

**Happy Testing! 🎉**
