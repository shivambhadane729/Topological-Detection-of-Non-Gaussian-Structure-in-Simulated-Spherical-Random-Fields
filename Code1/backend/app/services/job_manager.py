"""
CosmoPH - Job Manager Service
In-memory async job tracking. Production: swap for Celery + Redis.
"""
import uuid, time, threading
from typing import Optional, Any, Callable
from app.schemas.job import JobStatus

_jobs = {}
_lock = threading.Lock()

def create_job(job_type: str, params: dict = None) -> str:
    jid = str(uuid.uuid4())[:8]
    with _lock:
        _jobs[jid] = {
            "job_id": jid, "status": JobStatus.PENDING,
            "job_type": job_type, "parameters": params or {},
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "completed_at": None, "progress": 0.0,
            "message": "Job created", "result": None, "error": None,
        }
    return jid

def get_job(jid: str) -> Optional[dict]:
    with _lock:
        return _jobs.get(jid, {}).copy() if jid in _jobs else None

def update_job(jid: str, **kw):
    with _lock:
        if jid in _jobs:
            _jobs[jid].update(kw)

def run_job_async(jid: str, func: Callable, *args, **kwargs):
    """Run a function in a background thread and track its job status."""
    def _worker():
        update_job(jid, status=JobStatus.RUNNING, message="Processing...", progress=10.0)
        try:
            result = func(*args, **kwargs)
            update_job(jid, status=JobStatus.COMPLETED, result=result,
                       progress=100.0, message="Completed",
                       completed_at=time.strftime("%Y-%m-%dT%H:%M:%SZ"))
        except Exception as e:
            update_job(jid, status=JobStatus.FAILED, error=str(e),
                       message=f"Failed: {e}",
                       completed_at=time.strftime("%Y-%m-%dT%H:%M:%SZ"))
    t = threading.Thread(target=_worker, daemon=True)
    t.start()

def list_jobs(limit: int = 50) -> list:
    with _lock:
        jobs = list(_jobs.values())
    return sorted(jobs, key=lambda j: j['created_at'], reverse=True)[:limit]
