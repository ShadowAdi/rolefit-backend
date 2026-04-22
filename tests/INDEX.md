# Test Suite Index

## 📚 Documentation (Start Here!)

### For Quick Start
- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 3 steps ⚡
- **[run_tests.bat](run_tests.bat)** - Windows one-click testing 🪟

### For Complete Information
- **[README.md](README.md)** - Full documentation and guide 📖
- **[SETUP_SUMMARY.md](SETUP_SUMMARY.md)** - What's included and how it works 📋

## 🐍 Python Scripts

### Test Execution
1. **[test_resume_generation.py](test_resume_generation.py)** (Main Script)
   - Generates test users with unique credentials
   - Creates profiles and experiences
   - Tests resume generation API
   - ~650 lines of well-documented code
   - Run directly: `python test_resume_generation.py`

2. **[test_runner.py](test_runner.py)** (Advanced CLI)
   - Command-line interface with options
   - Customizable user count, URL, output
   - Export results to JSON
   - Run with options: `python test_runner.py --users 5 --export results.json`

3. **[health_check.py](health_check.py)** (Diagnostic)
   - Verifies server connectivity
   - Checks all required endpoints
   - Provides helpful error messages
   - Run first to diagnose issues: `python health_check.py`

### Support Files
- **[__init__.py](__init__.py)** - Python package initialization
- **[test_requirements.txt](test_requirements.txt)** - Python dependencies

### Batch Script
- **[run_tests.bat](run_tests.bat)** - Windows interactive menu (easiest for Windows users!)

## 🎯 Quick Navigation

### I want to...

**Run tests immediately** (Windows)
→ Double-click `run_tests.bat`

**Run tests immediately** (All platforms)
→ Run `python test_resume_generation.py`

**See what's included**
→ Read [SETUP_SUMMARY.md](SETUP_SUMMARY.md)

**Get started quickly**
→ Follow [QUICKSTART.md](QUICKSTART.md)

**Understand everything**
→ Read [README.md](README.md)

**Test with custom settings**
→ Use `python test_runner.py --help`

**Check if API is working**
→ Run `python health_check.py`

## 📊 Test Coverage

The test suite validates:

✅ **User Registration** - `/user/register`
✅ **User Authentication** - `/auth/login`
✅ **Profile Creation** - `/profile/` (POST)
✅ **Profile Retrieval** - `/profile/` (GET)
✅ **Experience Creation** - `/experience/` (POST)
✅ **Experience Retrieval** - `/experience/` (GET)
✅ **Job Description Creation** - `/job-descriptions/` (POST)
✅ **Resume Generation** - `/content/{jobId}` (POST)

## 🚀 Getting Started

1. **Ensure Backend is Running**
   ```bash
   cd ..
   python -m uvicorn main:app --reload
   ```

2. **Install Dependencies** (if needed)
   ```bash
   pip install -r test_requirements.txt
   ```

3. **Run Health Check** (recommended first)
   ```bash
   python health_check.py
   ```

4. **Run Tests**
   ```bash
   python test_resume_generation.py
   ```

## 📈 Features

- 🎯 **Automated Testing** - Entire workflow in one script
- 👥 **Multi-User Support** - Test with multiple users simultaneously
- 📊 **Detailed Reporting** - Success/failure counts and summaries
- 🔧 **Configurable** - Command-line arguments for flexibility
- 🏥 **Health Check** - Diagnostic tool for troubleshooting
- 🪟 **Windows Support** - Batch script with interactive menu
- 📁 **Well Documented** - Multiple documentation files
- ⚡ **Easy to Use** - Run in one command

## 📝 Example Commands

```bash
# Run with defaults (3 users)
python test_resume_generation.py

# Run with custom user count
python test_runner.py --users 10

# Export results to JSON
python test_runner.py --users 5 --export results.json

# Custom API URL
python test_runner.py --url http://localhost:8001/api/v1

# Verbose output
python test_runner.py --verbose

# Health check only
python health_check.py

# Health check with custom URL
python health_check.py http://localhost:8001/api/v1
```

## 📊 Expected Output

```
✓ User registered: testuser0_1234567890@testdomain.com
✓ User logged in: testuser0_1234567890@testdomain.com
✓ Profile created for testuser0_1234567890@testdomain.com
✓ Experience created: Senior Software Engineer at Tech Corp
✓ Resume generated successfully!
```

## ⚙️ System Requirements

- Python 3.7+
- requests library
- Running FastAPI backend server
- Network access to `http://localhost:8000`

## 🔧 Installation

```bash
# Install test dependencies
pip install -r test_requirements.txt

# Or install individually
pip install requests pytest pytest-asyncio
```

## 📞 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Cannot connect to server" | Start backend: `python -m uvicorn main:app --reload` |
| "Import error: requests" | Install: `pip install requests` |
| "Command not found: python" | Add Python to PATH or use `python3` |
| "Port 8000 already in use" | Kill existing process or use different port: `--port 8001` |

## 📋 Checklist Before Running

- [ ] Backend server is running
- [ ] Python 3.7+ is installed
- [ ] requests library is installed
- [ ] Database is initialized
- [ ] No firewalls blocking localhost:8000

## 🎓 Learning Value

These tests teach you:
- How to test REST APIs
- User registration/authentication flows
- JWT token handling
- Complex API workflows
- Error handling and reporting
- Professional test structure

## ✨ Test Quality

- **Lines of Code**: 1000+
- **Documentation**: Comprehensive
- **Error Handling**: Robust
- **Extensibility**: Easy to customize
- **Professional**: Production-ready structure

## 📞 Need Help?

1. **Quick Help** → Read [QUICKSTART.md](QUICKSTART.md)
2. **Detailed Help** → Read [README.md](README.md)
3. **See What's Inside** → Read [SETUP_SUMMARY.md](SETUP_SUMMARY.md)
4. **Check API** → Run `python health_check.py`
5. **Debug** → Check backend logs and test output

---

**Status**: ✅ Ready to Use  
**Created**: April 23, 2026  
**Test Suite Version**: 1.0
