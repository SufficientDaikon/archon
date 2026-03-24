"""Configuration file management for Archon CLI.

Manages ``~/.archon/config.yaml`` — the user-level configuration file
that stores preferences (FR-052 through FR-055, FR-061).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import yaml

from archon.utils.paths import get_archon_home, get_config_path, get_state_path


# ── Valid config keys and defaults ──────────────────────────────

VALID_KEYS: dict[str, Any] = {
    "default_platform": None,
    "output_format": "rich",      # "rich" | "plain" | "json"
    "telemetry": False,
    "verbose": False,
    "color": True,
    "archon_root": None,          # override root path
    "editor": None,               # preferred editor
}

VALID_KEY_NAMES = list(VALID_KEYS.keys())


# ── Config helpers ──────────────────────────────────────────────

def load_config() -> dict[str, Any]:
    """Load the config file; return defaults if missing or corrupt."""
    path = get_config_path()
    if not path.exists():
        return dict(VALID_KEYS)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        # Merge with defaults (config may be missing new keys)
        merged = dict(VALID_KEYS)
        merged.update({k: v for k, v in data.items() if k in VALID_KEYS})
        return merged
    except Exception:
        return dict(VALID_KEYS)


def save_config(cfg: dict[str, Any]) -> Path:
    """Persist configuration to disk."""
    path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        yaml.dump(cfg, fh, default_flow_style=False, sort_keys=False)
    return path


def get_config_value(key: str) -> Any:
    """Return the value for a single key (or KeyError if invalid)."""
    if key not in VALID_KEYS:
        raise KeyError(key)
    return load_config().get(key, VALID_KEYS[key])


def set_config_value(key: str, value: Any) -> Path:
    """Set a single config key and persist. Returns path to config file."""
    if key not in VALID_KEYS:
        raise KeyError(key)
    # Basic type coercion
    if isinstance(VALID_KEYS[key], bool):
        value = str(value).lower() in ("true", "1", "yes")
    cfg = load_config()
    cfg[key] = value
    return save_config(cfg)


def is_initialized() -> bool:
    """Return True if ``~/.archon/config.yaml`` exists."""
    return get_config_path().exists()


# ── Installation state ──────────────────────────────────────────

def load_state() -> dict[str, Any]:
    """Load the installation-state file (records of installed components)."""
    path = get_state_path()
    if not path.exists():
        return {"installed": []}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {"installed": []}
    except Exception:
        return {"installed": []}


def save_state(state: dict[str, Any]) -> None:
    path = get_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        yaml.dump(state, fh, default_flow_style=False, sort_keys=False)


def record_install(component_name: str, component_type: str, version: str,
                   platform: str, install_path: str) -> None:
    """Append an installation record to the state file (FR-067)."""
    from datetime import datetime
    state = load_state()
    records = state.setdefault("installed", [])
    # Upsert — replace if same (name, platform) combo
    records = [r for r in records if not (r.get("name") == component_name and r.get("platform") == platform)]
    records.append({
        "name": component_name,
        "type": component_type,
        "version": version,
        "platform": platform,
        "path": install_path,
        "installed_at": datetime.now().isoformat(),
    })
    state["installed"] = records
    save_state(state)


def remove_install_record(component_name: str, platform: str | None = None) -> int:
    """Remove installation record(s). Returns count removed."""
    state = load_state()
    before = len(state.get("installed", []))
    if platform:
        state["installed"] = [
            r for r in state.get("installed", [])
            if not (r.get("name") == component_name and r.get("platform") == platform)
        ]
    else:
        state["installed"] = [
            r for r in state.get("installed", [])
            if r.get("name") != component_name
        ]
    after = len(state["installed"])
    save_state(state)
    return before - after


def get_install_records(component_name: str | None = None, platform: str | None = None) -> list[dict]:
    """Query installation records with optional filters."""
    state = load_state()
    records = state.get("installed", [])
    if component_name:
        records = [r for r in records if r.get("name") == component_name]
    if platform:
        records = [r for r in records if r.get("platform") == platform]
    return records
