import functools
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path


def log_path() -> Path:
    return Path(os.environ.get("AUDIT_LOG_PATH", "audit_log.jsonl"))


def _write(record: dict) -> None:
    try:
        with log_path().open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    except OSError:
        pass  # un fallo del log no debe tumbar el tool


def audited(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        started = time.perf_counter()
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "tool": func.__name__,
            "args": list(args),
            "kwargs": kwargs,
        }
        try:
            result = func(*args, **kwargs)
            record["status"] = "ok"
            record["result"] = result
            return result
        except Exception as exc:
            record["status"] = "error"
            record["error"] = repr(exc)
            raise
        finally:
            record["duration_ms"] = round((time.perf_counter() - started) * 1000, 1)
            _write(record)

    return wrapper
