"""Hook invocation logging — one JSONL record per hook firing.

gcloud logs every CLI invocation to a file; this is the hook-layer analogue:
``<ARCHON_HOME>/logs/hooks-YYYY.MM.DD.jsonl``, one line per firing with the
hook name, project slug, duration, and hook-specific extras (tier/synapses
for the router, decisions for the guards, ...).

IRON RULE: logging is fail-open. Nothing in this module may ever raise into
a hook — a broken logs dir must not change any hook's exit code or stdout.
"""

import json
import os
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

_FILENAME_RE = re.compile(r"^hooks-(\d{4})\.(\d{2})\.(\d{2})\.jsonl$")


def _logs_dir() -> Path:
    env = os.environ.get("ARCHON_HOME")
    home = Path(env).expanduser() if env else Path.home() / ".archon"
    return home / "logs"


def write_record(
    hook: str,
    event: str,
    cwd: str | None,
    started_perf: float,
    ok: bool = True,
    error: str = "",
    **extra: Any,
) -> None:
    """Append one JSONL record for a hook firing. Never raises."""
    try:
        from shared.config import get_property
        from shared.state import project_slug

        if not get_property("logging/enabled", cwd):
            return

        record: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "hook": hook,
            "event": event,
            "project": project_slug(cwd) if cwd else "",
            "duration_ms": int((time.perf_counter() - started_perf) * 1000),
            "ok": ok,
        }
        if error:
            record["error"] = error
        record.update({k: v for k, v in extra.items() if v is not None})

        logs_dir = _logs_dir()
        logs_dir.mkdir(parents=True, exist_ok=True)
        filename = f"hooks-{datetime.now(timezone.utc).strftime('%Y.%m.%d')}.jsonl"
        with open(logs_dir / filename, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        pass  # fail-open by contract


def cleanup_old_logs(cwd: str | None = None) -> int:
    """Delete hook logs older than logging/max_log_days. Never raises.

    Age comes from the filename date, not mtime — cheap and unambiguous.
    Returns the number of files deleted (0 on any error).
    """
    deleted = 0
    try:
        from shared.config import get_property

        max_days = get_property("logging/max_log_days", cwd)
        cutoff = datetime.now(timezone.utc) - timedelta(days=max_days)
        logs_dir = _logs_dir()
        if not logs_dir.is_dir():
            return 0
        for path in logs_dir.iterdir():
            match = _FILENAME_RE.match(path.name)
            if not match:
                continue  # never touch foreign files
            try:
                file_date = datetime(
                    int(match.group(1)),
                    int(match.group(2)),
                    int(match.group(3)),
                    tzinfo=timezone.utc,
                )
                if file_date < cutoff:
                    path.unlink()
                    deleted += 1
            except (ValueError, OSError):
                continue
    except Exception:
        return deleted
    return deleted
