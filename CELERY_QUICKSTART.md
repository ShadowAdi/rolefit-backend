# Celery Quick Start Script

## One-Command Setup

### On Windows (PowerShell):

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start Redis (if not running)
# Option A: Using Docker (if installed)
docker run -d -p 6379:6379 redis:latest

# Option B: Download Redis from https://github.com/microsoftarchive/redis/releases
# Then: redis-server.exe

# 3. In separate terminals, run these 3 commands:

# Terminal 1: FastAPI Server
python main.py

# Terminal 2: Celery Worker
python run_celery_worker.py

# Terminal 3: (Optional) Monitor tasks
pip install flower
celery -A app.celery_app flower
# Visit: http://localhost:5555
```

### On Mac/Linux:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start Redis
# Option A: Using Docker
docker run -d -p 6379:6379 redis:latest

# Option B: Using Homebrew (Mac)
brew install redis
redis-server

# Option B: Using apt (Linux)
sudo apt-get install redis-server
redis-server

# 3. In separate terminals:

# Terminal 1
python main.py

# Terminal 2
python run_celery_worker.py

# Terminal 3 (Optional)
pip install flower
celery -A app.celery_app flower
```

---

## Testing Celery

### Using Python:

```python
from app.helpers.celery_helpers import QuickTasks, TaskHelper

# Submit a task
task_id = QuickTasks.generate_resume({...user_data...}, "...")
print(f"Task ID: {task_id}")

# Check status
status = TaskHelper.get_task_status(task_id)
print(f"Status: {status}")
```

### Using curl:

```bash
# Submit task
curl -X POST http://localhost:8000/api/v1/tasks/generate-resume \
  -H "Content-Type: application/json" \
  -d '{"user_data":{"name":"John"},"job_description":"Python developer"}'

# Check status (replace task_id with real ID)
curl http://localhost:8000/api/v1/tasks/status/task_id_here
```

---

## Troubleshooting

### "Redis connection refused"
```bash
# Check if Redis is running
redis-cli ping

# If not, start it:
redis-server  # Mac/Linux
# or
redis-server.exe  # Windows
```

### "No module named celery"
```bash
pip install celery==5.4.0
```

### "Worker not receiving tasks"
1. Make sure `run_celery_worker.py` is running
2. Check worker terminal output for errors
3. Make sure `REDIS_URL` is set in `.env`

---

## Common Commands

```bash
# Check all queued tasks
celery -A app.celery_app inspect active

# Purge (delete) all pending tasks
celery -A app.celery_app purge

# Gracefully shutdown workers
celery -A app.celery_app control shutdown
```
