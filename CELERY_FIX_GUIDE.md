# Celery Task Not Starting - Debugging & Fixes

## Issues Found & Fixed

### 1. ✅ FIXED: Missing `autodiscover_tasks()` in Celery Configuration
**File:** `app/core/celery_app.py`
- Added `celery_app.autodiscover_tasks(['app.tasks'])` to ensure tasks are discovered
- Added `broker_connection_retry_on_startup=True` to handle broker connection issues

### 2. ✅ FIXED: Explicit Task Import in Worker
**File:** `run_celery_worker.py`
- Changed from importing `app.tasks` (package) to explicitly importing `app.tasks.ai_tasks`
- Added logging of registered tasks when worker starts
- This ensures tasks are registered before the worker starts processing

### 3. ✅ ADDED: Comprehensive Logging in Tasks
**File:** `app/tasks/ai_tasks.py`
- Added logging at the start of `generate_resume_task` and throughout execution
- This helps identify where tasks are failing

## How to Test the Fix

### Step 1: Rebuild & Restart Docker Services
```bash
# If running in Docker
docker-compose down
docker-compose up --build
```

### Step 2: Verify Worker Registration
After the worker starts, look for this output:
```
[INFO/MainProcess] Connected to redis://redis:6379/1
[INFO/MainProcess] celery@... ready.
```

And check that your tasks are listed:
```
[tasks]
  . app.tasks.ai_tasks.cleanup_old_tasks
  . app.tasks.ai_tasks.generate_cover_letter_task
  . app.tasks.ai_tasks.generate_resume_task
```

### Step 3: Debug Script
Run the debug script to verify everything:
```bash
python debug_celery.py
```

This will check:
- Redis connectivity
- Celery configuration
- Registered tasks
- Task queuing capability

### Step 4: Monitor Task Execution
Watch the worker logs for messages like:
```
[resume] Task started - doc=... user=... job=...
[resume] Marked as processing - doc=...
[resume] Got job profile - doc=...
[resume] Built prompt - doc=...
[resume] Got response from Groq - doc=...
```

## Checklist to Verify Everything Works

- [ ] Docker containers are running (backend, celery-worker, postgres, redis)
- [ ] Celery worker shows "ready" status with 3+ tasks registered
- [ ] Call API to create resume → get doc_id and task_id
- [ ] Check celery worker logs for "[resume] Task started" message
- [ ] Wait for completion, then check GeneratedDocument table for resume_text

## If Tasks Still Don't Start

1. **Check Redis Connection**
   - Verify `REDIS_CELERY_URL` in `.env`
   - From container: `redis-cli -h redis ping` should return PONG

2. **Check Task Registration**
   - Run: `python debug_celery.py`
   - Should show 3+ registered tasks

3. **Check Broker Queue**
   - Use Redis CLI: `redis-cli KEYS '*'` to see queued tasks
   - Or: `redis-cli LRANGE celery 0 -1` to see celery queue

4. **Check Worker Logs**
   - Look for any "ERROR" or "FAILURE" messages
   - Check if task is actually being picked up

## Additional Configuration Notes

Your celery.conf now includes:
- `task_serializer="json"` - Tasks use JSON serialization
- `result_expires=3600` - Results stored for 1 hour
- `task_acks_late=True` - Worker acknowledges after task completes
- `broker_connection_retry_on_startup=True` - Handles connection issues

All of these settings are correct for your async resume generation use case.
