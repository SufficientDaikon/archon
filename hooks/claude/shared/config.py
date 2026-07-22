"""Archon properties — gcloud-style section/name configuration for the hook layer.

Single source of truth for every configurable hook knob. Stdlib only (hooks
import this directly; the archon CLI reaches it via core/hooks_bridge.py).

Precedence, highest first (mirrors gcloud's PropertySource chain):
  1. env var  — mechanically derived: ARCHON_{SECTION}_{NAME}
  2. project file — <cwd>/.archon/config          (INI)
  3. user file    — <ARCHON_HOME>/config          (INI)
  4. registry default

Malformed values never crash a hook — they fall back to the default.
"""

import configparser
import os
from pathlib import Path
from typing import Any, NamedTuple

USER_CONFIG_FILENAME = "config"
PROJECT_CONFIG_RELPATH = Path(".archon") / "config"

_TRUE_WORDS = {"1", "true", "yes", "on", "y"}
_FALSE_WORDS = {"0", "false", "no", "off", "n"}


class Property(NamedTuple):
    type: type
    default: Any
    help: str


# The registry. Keys are "section/name". Add new knobs here — nowhere else.
PROPERTIES: dict[str, Property] = {
    "classifier/trivial_max_words": Property(int, 12, "Word-count ceiling for TRIVIAL tier."),
    "classifier/simple_max_words": Property(int, 60, "Word-count ceiling for SIMPLE tier."),
    "classifier/moderate_max_words": Property(int, 300, "Word-count ceiling for MODERATE tier."),
    "classifier/complex_max_words": Property(int, 1000, "Word-count ceiling for COMPLEX tier."),
    "classifier/max_escalation": Property(int, 2, "Max tier bumps from keyword escalation."),
    "injection/enabled": Property(
        bool, True, "Master switch for synapse instruction injection (route tag still emitted)."
    ),
    "injection/metacognition": Property(bool, True, "Inject the metacognition synapse."),
    "injection/sequential_thinking": Property(
        bool, True, "Inject the sequential-thinking synapse."
    ),
    "injection/anti_rationalization": Property(
        bool, True, "Inject the anti-rationalization synapse."
    ),
    "injection/security_awareness": Property(bool, True, "Inject the security-awareness synapse."),
    "injection/pattern_recognition": Property(
        bool, True, "Inject the pattern-recognition synapse."
    ),
    "gate/enabled": Property(
        bool, True, "Completion gate blocks on failed tests/build (false: warn-only)."
    ),
    "gate/max_blocks": Property(int, 2, "Max completion-gate blocks per session before warn-only."),
    "scanner/extra_allowlist": Property(
        str, "", "Comma-separated extra file-path regexes exempt from secret scanning."
    ),
    "logging/enabled": Property(bool, True, "Write one JSONL record per hook firing."),
    "logging/max_log_days": Property(int, 30, "Delete hook logs older than this many days."),
    "logging/log_prompts": Property(
        bool, False, "Store the noise-stripped prompt in prompt_router log records."
    ),
    "logging/prompt_max_chars": Property(
        int, 500, "Cap on stored stripped-prompt length when log_prompts is enabled."
    ),
}


def _archon_home() -> Path:
    env = os.environ.get("ARCHON_HOME")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".archon"


def user_config_path() -> Path:
    return _archon_home() / USER_CONFIG_FILENAME


def project_config_path(cwd: str | None) -> Path | None:
    if not cwd:
        return None
    return Path(cwd) / PROJECT_CONFIG_RELPATH


def env_var_name(section: str, name: str) -> str:
    """Mechanical derivation, gcloud-style: ARCHON_{SECTION}_{NAME}."""
    return f"ARCHON_{section.upper()}_{name.upper()}"


def _coerce(raw: str, prop: Property) -> Any:
    """Parse a raw string into the property's type; fall back to default."""
    try:
        if prop.type is bool:
            word = raw.strip().lower()
            if word in _TRUE_WORDS:
                return True
            if word in _FALSE_WORDS:
                return False
            return prop.default
        if prop.type is int:
            return int(raw.strip())
        return raw
    except (ValueError, AttributeError):
        return prop.default


def _read_ini(path: Path | None) -> configparser.ConfigParser | None:
    if path is None or not path.is_file():
        return None
    parser = configparser.ConfigParser()
    try:
        parser.read(path, encoding="utf-8")
    except (configparser.Error, OSError, UnicodeDecodeError):
        return None
    return parser


def resolve_property(key: str, cwd: str | None = None) -> tuple[Any, str]:
    """Resolve one property. Returns (value, source) where source is
    "env" | "project" | "user" | "default". Unknown keys raise KeyError."""
    prop = PROPERTIES[key]
    section, name = key.split("/", 1)

    raw = os.environ.get(env_var_name(section, name))
    if raw is not None:
        return _coerce(raw, prop), "env"

    for parser, source in (
        (_read_ini(project_config_path(cwd)), "project"),
        (_read_ini(user_config_path()), "user"),
    ):
        if parser is not None and parser.has_option(section, name):
            return _coerce(parser.get(section, name), prop), source

    return prop.default, "default"


def get_property(key: str, cwd: str | None = None) -> Any:
    """Resolved value only. Unknown keys raise KeyError (a programming error)."""
    return resolve_property(key, cwd)[0]


def load_all(cwd: str | None = None) -> dict[str, tuple[Any, str]]:
    """Every registered property with its resolved (value, source)."""
    return {key: resolve_property(key, cwd) for key in sorted(PROPERTIES)}


def set_property(key: str, value: str, cwd: str | None = None, project: bool = False) -> Path:
    """Write a property to the user (default) or project INI file. CLI-only —
    hooks never write config. Returns the file written. Unknown keys raise
    KeyError; values are validated by round-tripping through _coerce."""
    prop = PROPERTIES[key]
    section, name = key.split("/", 1)

    if prop.type is bool and value.strip().lower() not in _TRUE_WORDS | _FALSE_WORDS:
        raise ValueError(f"{key} expects a boolean (true/false), got {value!r}")
    if prop.type is int:
        int(value.strip())  # raises ValueError on garbage

    if project:
        path = project_config_path(cwd or str(Path.cwd()))
    else:
        path = user_config_path()
    parser = _read_ini(path) or configparser.ConfigParser()
    if not parser.has_section(section):
        parser.add_section(section)
    parser.set(section, name, value)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        parser.write(fh)
    return path


def unset_property(key: str, cwd: str | None = None, project: bool = False) -> Path | None:
    """Remove a property from the user or project file. Returns the file
    modified, or None if it wasn't set there."""
    if key not in PROPERTIES:
        raise KeyError(key)
    section, name = key.split("/", 1)
    path = project_config_path(cwd or str(Path.cwd())) if project else user_config_path()
    parser = _read_ini(path)
    if parser is None or not parser.has_option(section, name):
        return None
    parser.remove_option(section, name)
    if not parser.options(section):
        parser.remove_section(section)
    with open(path, "w", encoding="utf-8") as fh:
        parser.write(fh)
    return path
