import threading
import time
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

# Simple In-Memory Task Queue
# In an advanced system, use a structure based on Supabase or Redis.
_task_queue = []
_completed_tasks = []
_worker_thread = None
_lock = threading.Lock()


def _worker_loop():
    """Background thread: Processes tasks in the queue."""
    while True:
        task = None
        with _lock:
            if _task_queue:
                # Get the first task with pending status
                for t in _task_queue:
                    if t["status"] == "pending":
                        if t.get("trigger_type") == "scheduled":
                            if (
                                t.get("schedule_time")
                                and datetime.now() >= t["schedule_time"]
                            ):
                                t["status"] = "running"
                                t["started_at"] = datetime.now()
                                task = t
                                break
                        else:
                            t["status"] = "running"
                            t["started_at"] = datetime.now()
                            task = t
                            break

        if task:
            try:
                # Autonomous Agent business logic
                import config
                from services.llm_service import chat_completion

                prompt = task.get("prompt", "")
                task_type = task.get("type", "general")
                logger.info(f"[Shadow Agent] Task Started: {task['id']} - {task_type}")

                # Simple/Complex processing simulation
                time.sleep(2)  # Process time simulation

                messages = [
                    {
                        "role": "system",
                        "content": "You are a task-oriented executive agent (Shadow Agent). Fulfill the requested task completely and thoroughly.",
                    },
                    {"role": "user", "content": prompt},
                ]

                # Send to Model (Default model as Fallback)
                model = config.AVAILABLE_MODELS.get(
                    "Google - Gemini 2.5 Flash", "google/gemini-2.5-flash"
                )
                response = chat_completion(
                    messages=messages, model=model, temperature=0.3, max_tokens=2048
                )

                with _lock:
                    task["status"] = "completed"
                    task["result"] = response
                    task["completed_at"] = datetime.now()
                    _completed_tasks.append(task)
                    _task_queue.remove(task)

                    # Re-queue if recurrent
                    if task.get("interval_minutes"):
                        from datetime import timedelta

                        next_run = datetime.now() + timedelta(
                            minutes=task["interval_minutes"]
                        )
                        new_task = dict(task)
                        new_task["id"] = str(uuid.uuid4())
                        new_task["status"] = "pending"
                        new_task["created_at"] = datetime.now()
                        new_task["result"] = None
                        new_task["error"] = None
                        new_task["schedule_time"] = next_run
                        new_task.pop("started_at", None)
                        new_task.pop("completed_at", None)
                        _task_queue.append(new_task)

                logger.info(f"[Shadow Agent] Task Completed: {task['id']}")

            except Exception as e:
                logger.error(f"[Shadow Agent] Task Error: {e}")
                with _lock:
                    task["status"] = "failed"
                    task["error"] = str(e)
                    task["completed_at"] = datetime.now()
                    _completed_tasks.append(task)
                    _task_queue.remove(task)
        else:
            time.sleep(5)  # Wait if queue is empty


def start_worker_if_needed():
    """Starts the thread if it is not already running."""
    global _worker_thread
    with _lock:
        if _worker_thread is None or not _worker_thread.is_alive():
            _worker_thread = threading.Thread(target=_worker_loop, daemon=True)
            _worker_thread.start()
            logger.info("Background Autonomous Agent (Shadow Agent) engine started.")


def add_task(
    task_type: str,
    prompt: str,
    user_id: str = None,
    trigger_type: str = "immediate",
    schedule_time: datetime = None,
    interval_minutes: int = None,
) -> str:
    """Adds a new task (job) to the queue."""
    start_worker_if_needed()
    task_id = str(uuid.uuid4())
    task = {
        "id": task_id,
        "type": task_type,
        "prompt": prompt,
        "status": "pending",
        "created_at": datetime.now(),
        "user_id": user_id,
        "result": None,
        "error": None,
        "trigger_type": trigger_type,
        "schedule_time": schedule_time,
        "interval_minutes": interval_minutes,
    }
    with _lock:
        _task_queue.append(task)
    return task_id


def get_all_tasks():
    """Returns all tasks (pending and completed)."""
    with _lock:
        return _task_queue + _completed_tasks


def get_task_status(task_id: str) -> dict:
    """Returns the status of a specific task."""
    with _lock:
        for t in _task_queue + _completed_tasks:
            if t["id"] == task_id:
                return t
    return None


def clear_completed_tasks():
    """Clears the history of completed tasks."""
    global _completed_tasks
    with _lock:
        _completed_tasks = []
