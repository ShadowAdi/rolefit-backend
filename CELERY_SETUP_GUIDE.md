# 🎯 Celery Setup Guide - Simple Explanation

## What is Celery?

Celery is a **task queue** that lets your FastAPI app run long-running operations in the background instead of making users wait.

### Real-world analogy:
- **Without Celery**: You order at a restaurant, chef cooks while you wait, you get food. (Slow!)
- **With Celery**: You order, get a receipt number, chef cooks in background. You check your receipt later to see if it's ready. (Fast!)

---

## Why Use Celery?

1. **AI API Calls** - Groq/Sarvam APIs take 5-30 seconds. Don't make users wait!
2. **PDF Generation** - Building PDFs takes time. Run in background!
3. **Better UX** - API returns immediately with a task ID
4. **Scalable** - Run multiple tasks in parallel

---

## Setup Steps

### Step 1: Install Dependencies
```bash
pip install celery==5.4.0
```

The `celery` package is already added to `requirements.txt`. Just run:
```bash
pip install -r requirements.txt
```

### Step 2: Check Your Redis Setup
Celery uses Redis as the message broker. Make sure Redis is running:
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG
```

If Redis isn't running, start it:
```bash
# Windows (if installed)
redis-server

# Or using Docker
docker run -d -p 6379:6379 redis:latest
```

### Step 3: Update Your `.env` File
Add this to your `.env`:
```
REDIS_URL=redis://localhost:6379/0
```

### Step 4: Files Created For You

✅ `app/celery_app.py` - Celery configuration
✅ `app/tasks/ai_tasks.py` - AI API background tasks
✅ `app/tasks/pdf_tasks.py` - PDF generation background tasks
✅ `app/helpers/celery_helpers.py` - Helper functions to use Celery
✅ `run_celery_worker.py` - Script to start the worker
✅ `run_celery_beat.py` - Script for periodic tasks

---

## How to Use Celery in Your Code

### Option 1: Quick & Easy (Recommended for beginners)

```python
from app.helpers.celery_helpers import QuickTasks

# In your FastAPI route:
@app.post("/generate-resume")
async def generate_resume(data: dict):
    # This returns IMMEDIATELY with a task ID
    # The actual generation happens in background
    task_id = QuickTasks.generate_resume(data["user_info"], data["job_desc"])
    
    return {
        "task_id": task_id,
        "status": "submitted",
        "message": "Resume generation started in background"
    }

# Check status later:
@app.get("/task-status/{task_id}")
async def check_status(task_id: str):
    status = TaskHelper.get_task_status(task_id)
    return status
```

### Option 2: Full Control

```python
from app.tasks.ai_tasks import generate_resume_with_ai

# Submit task
task = generate_resume_with_ai.delay(user_data, jd_content)

# Get task ID
print(f"Task ID: {task.id}")

# Check status
print(f"Task status: {task.status}")
print(f"Task result: {task.result}")
```

---

## Running Celery

You need to run 3 things:

### 1. FastAPI Server (as usual)
```bash
python main.py
# or
uvicorn main:app --reload
```

### 2. Celery Worker (NEW)
Open a new terminal and run:
```bash
python run_celery_worker.py
```

This worker listens for tasks and executes them.

### 3. (Optional) Celery Beat Scheduler
For periodic tasks (like cleanup every hour):
```bash
python run_celery_beat.py
```

---

## Task Lifecycle (Visual)

```
1. User calls API endpoint
   ↓
2. FastAPI route submits task to Celery
   ↓
3. API returns immediately with task_id: "abc123"
   ↓
4. Celery Worker picks up task from Redis queue
   ↓
5. Worker executes the task (AI call, PDF generation, etc)
   ↓
6. Result stored in Redis
   ↓
7. User checks status with task_id
   ↓
8. User gets result when ready!
```

---

## Complete Example

### Setup (do once):
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Make sure Redis is running
redis-cli ping  # Should return: PONG

# 3. Set REDIS_URL in .env
# REDIS_URL=redis://localhost:6379/0
```

### Run (every time):
```bash
# Terminal 1: FastAPI server
python main.py

# Terminal 2: Celery worker
python run_celery_worker.py

# Terminal 3: Celery beat (optional)
python run_celery_beat.py
```

### Test API:
```bash
# 1. Submit task
curl -X POST http://localhost:8000/api/v1/tasks/generate-resume \
  -H "Content-Type: application/json" \
  -d '{"user_data": {...}, "job_description": "..."}'

# Response:
# {
#   "task_id": "abc123xyz",
#   "status": "submitted",
#   "message": "Resume generation started"
# }

# 2. Check status
curl http://localhost:8000/api/v1/tasks/status/abc123xyz

# Response (while running):
# {
#   "task_id": "abc123xyz",
#   "status": "PROGRESS",
#   "progress": "50%"
# }

# Response (when done):
# {
#   "task_id": "abc123xyz",
#   "status": "SUCCESS",
#   "result": {...generated resume...}
# }
```

---

## Key Concepts

| Term | Meaning |
|------|---------|
| **Task** | A function that runs in background (e.g., generate_resume) |
| **Queue** | Where tasks wait to be processed (Redis stores this) |
| **Worker** | The process that executes tasks (run_celery_worker.py) |
| **Broker** | The message system (Redis in our case) |
| **Task ID** | Unique identifier for each task |
| **Status** | Current state: PENDING, PROGRESS, SUCCESS, FAILURE |

---

## Task Statuses Explained

| Status | Meaning | What to do |
|--------|---------|-----------|
| **PENDING** | Task is waiting in queue | Wait and check again |
| **PROGRESS** | Task is running | Show progress bar to user |
| **SUCCESS** | Task completed! | Return result to user |
| **FAILURE** | Task failed | Show error to user |
| **RETRY** | Task is being retried | Wait and check again |

---

## Common Issues & Fixes

### Issue: "Connection refused" error
**Cause**: Redis not running
**Fix**: Start Redis (`redis-server` or Docker)

### Issue: "No celery app found"
**Cause**: Worker can't find task definitions
**Fix**: Make sure `app/celery_app.py` exists and imports tasks

### Issue: Tasks not executing
**Cause**: Worker not running
**Fix**: Run `python run_celery_worker.py` in separate terminal

### Issue: Tasks very slow
**Cause**: Not enough workers
**Fix**: Increase `--concurrency` in `run_celery_worker.py`

---

## Advanced: Docker Compose (Optional)

If you want Celery to run in Docker:

```yaml
# Add to docker-compose.yml
celery:
  build: .
  command: python run_celery_worker.py
  environment:
    - REDIS_URL=redis://redis:6379/0
  depends_on:
    - redis
```

---

## Next Steps

1. ✅ Install Celery (`pip install -r requirements.txt`)
2. ✅ Make sure Redis is running
3. ✅ Add routes from `app/api/v1/celery_examples.py` to your router
4. ✅ Run: `python main.py` in one terminal
5. ✅ Run: `python run_celery_worker.py` in another terminal
6. ✅ Test with: `curl http://localhost:8000/api/v1/tasks/generate-resume`

---

## Monitoring (Optional)

To see what tasks are running:
```bash
# Requires flower
pip install flower

# Run:
celery -A app.celery_app flower
```

Then visit: http://localhost:5555

---

## Questions?

Read the files:
- `app/celery_app.py` - Has comments explaining configuration
- `app/tasks/ai_tasks.py` - Shows how AI tasks work
- `app/tasks/pdf_tasks.py` - Shows how PDF tasks work
- `app/helpers/celery_helpers.py` - Helper functions with examples
