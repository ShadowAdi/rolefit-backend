# Resume Generation Test Suite

This folder contains test scripts for the Rolefit Backend API, specifically for testing the resume generation flow.

## Overview

The test suite validates the complete workflow:
1. **User Registration** - Creates test users with email and password
2. **User Login** - Authenticates users and retrieves access tokens
3. **Profile Creation** - Creates user profiles with basic information
4. **Experience Addition** - Adds multiple work experiences for each user
5. **Job Description Creation** - Creates job postings for testing
6. **Resume Text Generation** - Generates resume text matching user experience to job descriptions

## Files

### `test_resume_generation.py`
Main test script that orchestrates the complete resume generation flow.

**Features:**
- Creates multiple test users automatically
- Manages user authentication and token handling
- Creates profiles and experience records
- Tests resume text generation via the content API
- Provides detailed test results and error reporting

## Requirements

Before running the tests, ensure you have:

1. **Backend Server Running**
   ```bash
   cd c:\Users\lenovo\Desktop\rolefit\rolefit-backend
   python -m uvicorn main:app --reload
   ```

2. **Required Python Packages**
   ```bash
   pip install requests
   ```

## Configuration

You can modify the test script to adjust:

- **BASE_URL**: Change the server URL (default: `http://localhost:8000/api/v1`)
- **USERS_COUNT**: Number of test users to create (default: 3)
- **Test Data**: Customize the profile and experience data in the script

## Running the Tests

### Option 1: Direct Execution
```bash
cd c:\Users\lenovo\Desktop\rolefit\rolefit-backend
python tests/test_resume_generation.py
```

### Option 2: From Project Root
```bash
cd c:\Users\lenovo\Desktop\rolefit
python -m tests.test_resume_generation
```

### Option 3: Using pytest (if installed)
```bash
pip install pytest
pytest tests/test_resume_generation.py -v
```

## Expected Output

The script will display:
- ✓ Successful operations (green checkmarks)
- ✗ Failed operations (red X marks)
- Test summary with statistics
- List of any failed operations with error messages

Example output:
```
======================================================================
RESUME GENERATION TEST - COMPLETE FLOW
======================================================================

📋 Step 1: Generating test users...
Generated 3 test user credentials

👤 Processing User 1/3
----------------------------------------------------------------------
✓ User registered: testuser0_1234567890@testdomain.com (ID: abc123...)
✓ User logged in: testuser0_1234567890@testdomain.com
✓ Profile created for testuser0_1234567890@testdomain.com (Profile ID: xyz789...)
  Adding experience data...
✓ Experience created: Senior Software Engineer at Tech Corp
✓ Experience created: Full Stack Developer at StartUp Inc

======================================================================
TEST SUMMARY
======================================================================
Users Created:       3/3
Profiles Created:    3/3
Experiences Created: 6
Resumes Generated:   3
✓ All operations completed successfully!
```

## Troubleshooting

### Connection Error
If you see `Cannot connect to server at http://localhost:8000/api/v1`:
- Start the backend server first
- Check if the URL is correct
- Verify no firewall is blocking the connection

### Authentication Error (401)
- Check if the user registration succeeded
- Verify the login token is being retrieved correctly
- Ensure the Authorization header format is correct: `Bearer <token>`

### Validation Errors (422)
- Check email format (must be valid email)
- Verify password meets requirements
- Ensure all required fields are provided with valid values

### Resume Generation Not Working
- Verify the profile has been created
- Ensure experiences have been added
- Check that a valid job ID exists
- Review the backend logs for more details

## Data Persistence

The test script creates **real data** in your database:
- Test users will remain in the database
- Profiles and experiences will be associated with these test users
- You can delete them manually or create a cleanup function

To safely test without persisting data, consider:
1. Using a test database (separate from production)
2. Adding a cleanup function to the test script
3. Using database transactions that rollback after tests

## Future Enhancements

Consider adding:
- Database cleanup/rollback functionality
- Performance benchmarking
- Batch testing with configurable parameters
- CSV export of test results
- API response validation
- Content comparison tests (resume text quality)
